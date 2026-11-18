// helper functions for verifying a ballot
// assumes all of Helios machinery is loaded

function verify_ballot(election_raw_json, encrypted_vote_json, status_cb) {
    var overall_result = true;
    try {
	election = HELIOS.Election.fromJSONString(election_raw_json);
	var election_hash = election.get_hash();
	status_cb(T("election fingerprint is %(hash)s", {hash: election_hash}));
	
	// display ballot fingerprint
	encrypted_vote = HELIOS.EncryptedVote.fromJSONObject(encrypted_vote_json, election);
	status_cb(T("ballot tracker is %(hash)s", {hash: encrypted_vote.get_hash()}));
	
      // check the hash
      if (election_hash == encrypted_vote.election_hash) {
          status_cb(T("election fingerprint matches ballot"));
      } else {
          overall_result = false;
          status_cb(T("PROBLEM = election fingerprint does not match"));          
      }
      
      // display the ballot as it is claimed to be
      status_cb(T("Ballot Contents:"));
      _(election.questions).each(function(q, qnum) {
	      if (q.tally_type != "homomorphic") {
		  status_cb(T("WARNING: the tally type for this question is not homomorphic. Verification may fail because this verifier is only set up to handle homomorphic ballots."));
	      }
        
	      var answer_pretty_list = _(encrypted_vote.encrypted_answers[qnum].answer).map(function(aindex, anum) {
		      return q.answers[aindex];
		  });
	      status_cb(T("Question #%(num)s - %(name)s : %(answers)s", {num: qnum+1, name: q.short_name, answers: answer_pretty_list.join(", ")}));
      });
      
      // verify the encryption
      if (encrypted_vote.verifyEncryption(election.questions, election.public_key)) {
          status_cb(T("Encryption Verified"));
      } else {
          overall_result = false;
          status_cb(T("PROBLEM = Encryption doesn't match."));
      }
      
      // verify the proofs
      if (encrypted_vote.verifyProofs(election.public_key, function(ea_num, choice_num, result) {
      })) {
          status_cb(T("Proofs ok."));
      } else {
          overall_result = false;
          status_cb(T("PROBLEM = Proofs don't work."));
      }
    } catch (e) {
      status_cb(T('problem parsing election or ballot data structures, malformed inputs: %(error)s', {error: e.toString()}));
      overall_result=false;
    }

    return overall_result;
}
