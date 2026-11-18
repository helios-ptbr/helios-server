/**
 * Helios Timezone Display Utility
 * Uses built-in browser Intl API for timezone conversion
 */

var HeliosTimezone = (function() {
  'use strict';

  // Language of the page (<html lang>), so dates read right in each language.
  // Falls back to English if the browser does not know it.
  function pageLocale() {
    var lang = document.documentElement.lang || 'en-US';
    try {
      Intl.DateTimeFormat.supportedLocalesOf([lang]);
      return lang;
    } catch (e) {
      return 'en-US';
    }
  }
  var LOCALE = pageLocale();

  // Texts come from the page (translated by Django); English is the default.
  var TEXTS = {
    utcTitle: 'Universal Coordinated Time',
    localTitle: 'Your local timezone',
    thisTimeIs: 'This time is:',
    // %(tz)s is the browser's time zone, e.g. "BRT (UTC-03:00)"
    inputHelp: 'Enter the date and time in your browser time zone (%(tz)s). Helios stores it in UTC.',
    balloon: 'Your browser time zone is %(tz)s. Anyone in another time zone, for example one hour or two hours behind, types the time shown by their own browser: Helios converts it to UTC. If this zone is wrong, fix the time zone of your computer.'
  };
  var fromPage = window.HELIOS_TZ_TEXTS || {};
  for (var key in TEXTS) {
    if (Object.prototype.hasOwnProperty.call(fromPage, key) && typeof fromPage[key] === 'string') {
      TEXTS[key] = fromPage[key];
    }
  }

  // Module configuration
  var config = {
    utcFormatter: new Intl.DateTimeFormat(LOCALE, {
      timeZone: 'UTC',
      year: 'numeric',
      month: 'short',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    }),
    localFormatter: new Intl.DateTimeFormat(LOCALE, {
      year: 'numeric',
      month: 'short',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    })
  };

  function escapeHtml(text) {
    return String(text).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function escapeAttr(text) {
    return escapeHtml(text).replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  /**
   * Get local timezone name/abbreviation using Intl API
   * @returns {string} Timezone abbreviation or 'Local'
   */
  function getLocalTimezoneName() {
    try {
      var formatter = new Intl.DateTimeFormat(LOCALE, {
        timeZoneName: 'short'
      });
      var parts = formatter.formatToParts(new Date());
      var tzPart = parts.find(function(part) { return part.type === 'timeZoneName'; });
      return tzPart ? tzPart.value : 'Local';
    } catch (e) {
      return 'Local';
    }
  }

  /**
   * Parse UTC datetime string into Date object
   * @param {string} utcDateStr - UTC datetime string
   * @returns {Date|null} Date object or null if invalid
   */
  function parseUTCDate(utcDateStr) {
    if (!utcDateStr || typeof utcDateStr !== 'string') {
      return null;
    }

    // Try parsing with ' UTC' suffix first
    var date = new Date(utcDateStr + ' UTC');

    if (isNaN(date.getTime())) {
      // Try without ' UTC' suffix
      date = new Date(utcDateStr);
      if (isNaN(date.getTime())) {
        return null;
      }
    }

    return date;
  }

  /**
   * Check if user is in UTC timezone
   * @param {Date} date - Date object to check
   * @returns {boolean} True if in UTC timezone
   */
  function isUTCTimezone(date) {
    return date.getTimezoneOffset() === 0;
  }

  /**
   * Create timezone display HTML
   * @param {Date} date - Date object to format
   * @returns {string} HTML string for display
   */
  function createTimezoneHTML(date) {
    var utcFormatted = config.utcFormatter.format(date);
    var localFormatted = config.localFormatter.format(date);
    var localTz = getLocalTimezoneName();

    if (isUTCTimezone(date)) {
      return '<strong>' + utcFormatted + ' UTC</strong>';
    }

    return '<span class="tz-utc" title="' + escapeAttr(TEXTS.utcTitle) + '">' +
           utcFormatted + ' UTC</span>' +
           '<span class="tz-separator"> / </span>' +
           '<span class="tz-local" title="' + escapeAttr(TEXTS.localTitle) + '">' +
           localFormatted + ' ' + localTz + '</span>';
  }

  /**
   * Convert a UTC timestamp element to show both UTC and local time
   * @param {HTMLElement} element - Element to convert
   */
  function convertTimestamp(element) {
    if (!element || element.classList.contains('tz-converted')) {
      return;
    }

    var utcDateStr = element.getAttribute('data-utc-time') || element.textContent.trim();
    var date = parseUTCDate(utcDateStr);

    if (!date) {
      console.warn('[HeliosTimezone] Could not parse datetime:', utcDateStr);
      return;
    }

    // Create and insert the display
    var container = document.createElement('span');
    container.className = 'tz-display';
    container.innerHTML = createTimezoneHTML(date);

    // Replace element content
    element.innerHTML = '';
    element.appendChild(container);
    element.classList.add('tz-converted');
  }

  /**
   * Create helper text HTML for datetime input
   * @param {Date} date - Date object to format
   * @returns {string} HTML string for helper text
   */
  function createHelperHTML(date) {
    var utcFormatted = config.utcFormatter.format(date);
    var localFormatted = config.localFormatter.format(date);
    var localTz = getLocalTimezoneName();

    if (isUTCTimezone(date)) {
      return '<small>' + escapeHtml(TEXTS.thisTimeIs) + ' <strong>' + utcFormatted + ' UTC</strong></small>';
    }

    return '<small>' + escapeHtml(TEXTS.thisTimeIs) + ' <strong>' + utcFormatted + ' UTC</strong> / ' +
           '<strong>' + localFormatted + ' ' + localTz + '</strong></small>';
  }

  // ---- datetime-local fields -------------------------------------------------
  // The server keeps and expects UTC. The person types in the browser's time zone:
  // on load the UTC value is shown as local time, and on submit the local value
  // goes back to the server as UTC. The server code does not change.

  function pad(n) {
    return (n < 10 ? '0' : '') + n;
  }

  function formatInputValue(date, utc) {
    var y = utc ? date.getUTCFullYear() : date.getFullYear();
    var mo = (utc ? date.getUTCMonth() : date.getMonth()) + 1;
    var d = utc ? date.getUTCDate() : date.getDate();
    var h = utc ? date.getUTCHours() : date.getHours();
    var mi = utc ? date.getUTCMinutes() : date.getMinutes();
    return y + '-' + pad(mo) + '-' + pad(d) + 'T' + pad(h) + ':' + pad(mi);
  }

  // "2026-12-01T09:00" typed as local time -> Date
  function localInputToDate(value) {
    var m = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/.exec(value || '');
    if (!m) { return null; }
    var date = new Date(+m[1], +m[2] - 1, +m[3], +m[4], +m[5]);
    return isNaN(date.getTime()) ? null : date;
  }

  // "2026-12-01T12:00" sent by the server as UTC -> Date
  function utcInputToDate(value) {
    var m = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/.exec(value || '');
    if (!m) { return null; }
    var date = new Date(Date.UTC(+m[1], +m[2] - 1, +m[3], +m[4], +m[5]));
    return isNaN(date.getTime()) ? null : date;
  }

  function offsetLabel(date) {
    var off = -date.getTimezoneOffset();
    var sign = off < 0 ? '-' : '+';
    off = Math.abs(off);
    return 'UTC' + sign + pad(Math.floor(off / 60)) + ':' + pad(off % 60);
  }

  function zoneLabel() {
    var now = new Date();
    return getLocalTimezoneName() + ' (' + offsetLabel(now) + ')';
  }

  function helpTextFor(input) {
    var text = TEXTS.inputHelp.replace('%(tz)s', zoneLabel());
    var id = (input.getAttribute('aria-describedby') || '').split(' ')[0];
    var el = id ? document.getElementById(id) : null;
    if (el) { el.textContent = text; }
  }

  // Balloon with the browser's time zone, at the end of the help text line (hover, focus or tap)
  function addBalloon(input) {
    var id = (input.getAttribute('aria-describedby') || '').split(' ')[0];
    var help = id ? document.getElementById(id) : null;
    var anchor = help || input;
    var next = anchor.nextElementSibling;
    if (next && next.classList.contains('tz-balloon')) { return; }
    // the <br> between the field and its help text is not needed: the field is a block
    if (help && help.previousElementSibling && help.previousElementSibling.tagName === 'BR') {
      help.parentNode.removeChild(help.previousElementSibling);
    }
    var balloon = document.createElement('span');
    balloon.className = 'tz-balloon';
    balloon.tabIndex = 0;
    balloon.setAttribute('role', 'note');
    balloon.setAttribute('aria-label', TEXTS.balloon.replace('%(tz)s', zoneLabel()));
    balloon.setAttribute('data-balloon', TEXTS.balloon.replace('%(tz)s', zoneLabel()));
    balloon.textContent = '\u24D8';
    anchor.parentNode.insertBefore(balloon, anchor.nextSibling);
  }

  function convertInputToLocal(input) {
    if (input.getAttribute('data-tz-local')) { return; }
    var date = utcInputToDate(input.value);
    if (date) { input.value = formatInputValue(date, false); }
    input.setAttribute('data-tz-local', '1');
    helpTextFor(input);
    addBalloon(input);
  }

  function submitAsUtc(form) {
    Array.prototype.forEach.call(form.querySelectorAll('input[type="datetime-local"][data-tz-local]'), function(input) {
      var name = input.getAttribute('name');
      if (!name) { return; }
      var hidden = document.createElement('input');
      hidden.type = 'hidden';
      hidden.name = name;
      var date = localInputToDate(input.value);
      hidden.value = date ? formatInputValue(date, true) : input.value;
      hidden.setAttribute('data-tz-utc-copy', '1');
      input.setAttribute('data-orig-name', name);
      input.removeAttribute('name');
      form.appendChild(hidden);
    });
  }

  // back button: the page comes back from cache with the names swapped, put them back
  function restoreAfterSubmit() {
    Array.prototype.forEach.call(document.querySelectorAll('input[data-tz-utc-copy]'), function(h) {
      h.parentNode.removeChild(h);
    });
    Array.prototype.forEach.call(document.querySelectorAll('input[data-orig-name]'), function(input) {
      input.setAttribute('name', input.getAttribute('data-orig-name'));
      input.removeAttribute('data-orig-name');
    });
  }

  /**
   * Update datetime-local input helper text
   * @param {HTMLInputElement} input - Input element to update
   */
  function updateDateTimeInputHelper(input) {
    if (!input || !input.value) {
      return;
    }

    // The field holds the browser's local time (format: YYYY-MM-DDTHH:MM)
    var date = localInputToDate(input.value);

    if (!date) {
      return;
    }

    // Get or create helper element
    var helper = input.nextElementSibling;
    if (!helper || !helper.classList.contains('tz-input-helper')) {
      helper = document.createElement('div');
      helper.className = 'tz-input-helper';
      input.parentNode.insertBefore(helper, input.nextSibling);
    }

    helper.innerHTML = createHelperHTML(date);
  }

  /**
   * Initialize timezone display for all timestamp elements
   */
  function initTimestampElements() {
    var elements = document.querySelectorAll('[data-utc-time]');
    Array.prototype.forEach.call(elements, convertTimestamp);
  }

  /**
   * Initialize datetime input helpers
   */
  function initDateTimeInputs() {
    var datetimeInputs = document.querySelectorAll('input[type="datetime-local"]');

    Array.prototype.forEach.call(datetimeInputs, function(input) {
      convertInputToLocal(input);

      // Update helper on input change
      input.addEventListener('change', function() {
        updateDateTimeInputHelper(this);
      });

      // Update helper on page load if there's a value
      if (input.value) {
        updateDateTimeInputHelper(input);
      }
    });

    var forms = [];
    Array.prototype.forEach.call(datetimeInputs, function(input) {
      if (input.form && forms.indexOf(input.form) === -1) { forms.push(input.form); }
    });
    forms.forEach(function(form) {
      form.addEventListener('submit', function() { submitAsUtc(form); });
    });
    window.addEventListener('pageshow', function(event) {
      if (event.persisted) { restoreAfterSubmit(); }
    });
  }

  /**
   * Initialize all timezone display functionality
   */
  function init() {
    initTimestampElements();
    initDateTimeInputs();
  }

  // Auto-initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Public API
  return {
    init: init,
    convertTimestamp: convertTimestamp,
    updateDateTimeInputHelper: updateDateTimeInputHelper,
    parseUTCDate: parseUTCDate,
    getLocalTimezoneName: getLocalTimezoneName,
    createTimezoneHTML: createTimezoneHTML,
    createHelperHTML: createHelperHTML
  };
})();
