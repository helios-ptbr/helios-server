"""
Background tasks for Helios, run by the database task worker

2010-08-01
ben@adida.net
"""
import copy
import logging
from django.conf import settings
from django.utils.translation import gettext, ngettext
from django.urls import reverse
from django_tasks import task
from urllib.parse import urlparse

from . import signals
from . import utils
from .models import CastVote, Election, Voter, VoterFile, EmailOptOut
from .view_utils import render_text_template


@task(priority=10)  # ahead of bulk voter emails
def cast_vote_verify_and_store(cast_vote_id, status_update_message=None, **kwargs):
    cast_vote = CastVote.objects.get(id=cast_vote_id)
    result = cast_vote.verify_and_store()

    voter = cast_vote.voter
    election = voter.election
    user = voter.get_user()

    if result:
        # send the signal
        signals.vote_cast.send(sender=election, election=election, user=user, voter=voter, cast_vote=cast_vote)

        if status_update_message and user.can_update_status():
            user.update_status(status_update_message)
    else:
        logger = logging.getLogger(__name__)
        logger.error("Failed to verify and store %d" % cast_vote_id)


@task()
def voters_email(election_id, subject_template, body_template, extra_vars={},
                 voter_constraints_include=None, voter_constraints_exclude=None):
    """
    voter_constraints_include are conditions on including voters
    voter_constraints_exclude are conditions on excluding voters
    """
    election = Election.objects.get(id=election_id)

    # select the right list of voters
    voters = election.voter_set.all()
    if voter_constraints_include:
        voters = voters.filter(**voter_constraints_include)
    if voter_constraints_exclude:
        voters = voters.exclude(**voter_constraints_exclude)

    for voter in voters:
        single_voter_email.enqueue(voter.uuid, subject_template, body_template, extra_vars)


@task()
def voters_notify(election_id, notification_template, extra_vars={}):
    election = Election.objects.get(id=election_id)
    for voter in election.voter_set.all():
        single_voter_notify.enqueue(voter.uuid, notification_template, extra_vars)


@task()
def single_voter_email(voter_uuid, subject_template, body_template, extra_vars={}):
    voter = Voter.objects.get(uuid=voter_uuid)
    
    # Check if voter email is opted out
    voter_email = voter.voter_email or (voter.user and voter.user.user_id)
    if voter_email and EmailOptOut.is_opted_out(voter_email):
        logger = logging.getLogger(__name__)
        logger.info(f"Skipping email to opted-out voter {voter.uuid}")
        return

    the_vars = copy.copy(extra_vars)
    the_vars.update({'election': voter.election})
    the_vars.update({'voter': voter})
    
    # Add unsubscribe link to email context
    if voter_email:
        unsubscribe_code = utils.generate_email_confirmation_code(voter_email, 'optout')
        unsubscribe_path = reverse('optout_confirm', kwargs={'email': voter_email, 'code': unsubscribe_code})
        unsubscribe_url = f"{settings.URL_HOST}{unsubscribe_path}"
        
        the_vars.update({
            'unsubscribe_url': unsubscribe_url,
            'unsubscribe_code': unsubscribe_code
        })

    subject = render_text_template(subject_template, the_vars)
    body = render_text_template(body_template, the_vars)

    voter.send_message(subject, body)


@task()
def single_voter_notify(voter_uuid, notification_template, extra_vars={}):
    voter = Voter.objects.get(uuid=voter_uuid)

    the_vars = copy.copy(extra_vars)
    the_vars.update({'voter': voter})

    notification = render_text_template(notification_template, the_vars)

    voter.send_notification(notification)


@task()
def election_compute_tally(election_id):
    election = Election.objects.get(id=election_id)
    election.compute_tally()

    election_notify_admin.enqueue(election_id=election_id,
                                subject=gettext("encrypted tally computed"),
                                body=gettext("""
The encrypted tally for election %(election)s has been computed.

--
Helios
""") % {'election': election.name})

    if election.has_helios_trustee():
        tally_helios_decrypt.enqueue(election_id=election.id)


@task()
def tally_helios_decrypt(election_id):
    election = Election.objects.get(id=election_id)
    election.helios_trustee_decrypt()
    election_notify_admin.enqueue(election_id=election_id,
                                subject=gettext('Helios Decrypt'),
                                body=gettext("""
Helios has decrypted its portion of the tally
for election %(election)s.

--
Helios
""") % {'election': election.name})


@task()
def voter_file_process(voter_file_id):
    voter_file = VoterFile.objects.get(id=voter_file_id)
    # a requeued task may find the file already processed; reprocessing would reset its counts
    if voter_file.processing_finished_at:
        return
    voter_file.process()

    skipped = ""
    if voter_file.num_skipped:
        skipped = ngettext("""
1 row in the file was not added, because those voters were already
on the voter list (or listed twice in the file), or have opted out of
Helios emails. Opted-out voters are listed in a separate email.
""", """
%(n)d rows in the file were not added, because those voters were already
on the voter list (or listed twice in the file), or have opted out of
Helios emails. Opted-out voters are listed in a separate email.
""", voter_file.num_skipped) % {'n': voter_file.num_skipped}

    election_notify_admin.enqueue(election_id=voter_file.election.id,
                                subject=gettext('voter file processed'),
                                body=gettext("""
Your voter file upload for election %(election)s
has been processed.

""") % {'election': voter_file.election.name} + ngettext("1 voter has been created.", "%(n)d voters have been created.",
                                                       voter_file.num_voters) % {'n': voter_file.num_voters} + """
%s
--
Helios
""" % skipped)


@task()
def notify_admin_opted_out_voters(election_id, opted_out_voters):
    election = Election.objects.get(id=election_id)
    
    if not opted_out_voters:
        return
    
    subject = gettext("Opted-out voters not added to election %(election)s") % {'election': election.name}
    
    body = gettext("""
The following %(n)d voters could not be added to election "%(election)s" 
because they have opted out of receiving Helios emails:

""") % {'n': len(opted_out_voters), 'election': election.name}
    
    for voter in opted_out_voters:
        body += gettext("- %(name)s (%(email)s) [ID: %(voter_id)s, Type: %(voter_type)s]") % {
            'name': voter['name'], 'email': voter['email'], 'voter_id': voter['voter_id'], 'voter_type': voter['voter_type']} + "\n"
    
    optin_path = reverse('optin_form')
    optin_url = f"{settings.URL_HOST}{optin_path}"
    
    body += gettext("""

These voters will need to opt back in before they can be added to elections.
They can opt back in at: %(url)s

--
Helios
""") % {'url': optin_url}
    
    election.admin.send_message(subject, body)


@task()
def election_notify_admin(election_id, subject, body):
    election = Election.objects.get(id=election_id)
    election.admin.send_message(subject, body)
