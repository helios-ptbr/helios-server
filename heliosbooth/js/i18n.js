// Helios booth i18n. Fixed file: no URL logic, no code loading.
// A page like vote.pt-BR.html loads strings.<lang>.js (data only) before this.
var BOOTH_STRINGS = (typeof BOOTH_STRINGS === "undefined") ? {} : BOOTH_STRINGS;
function T(s) {
  return Object.prototype.hasOwnProperty.call(BOOTH_STRINGS, s) ? BOOTH_STRINGS[s] : s;
}
