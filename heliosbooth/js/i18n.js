// Helios booth i18n. Fixed file: no URL logic, no code loading.
// A page like vote.pt-BR.html loads strings.<lang>.js (data only) before this.
// T("text %(name)s", {name: value}) returns the translation, or the English
// text when there is none. Values are put in as plain text.
var BOOTH_STRINGS = (typeof BOOTH_STRINGS === "undefined") ? {} : BOOTH_STRINGS;
function T(s, vars) {
  var out = Object.prototype.hasOwnProperty.call(BOOTH_STRINGS, s) ? BOOTH_STRINGS[s] : s;
  if (vars) {
    out = out.replace(/%\(([A-Za-z_][A-Za-z0-9_]*)\)s/g, function (m, name) {
      return Object.prototype.hasOwnProperty.call(vars, name) ? String(vars[name]) : m;
    });
  }
  return out;
}
