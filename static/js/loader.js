(function () {
  var loader = null;
  function ensureLoader() {
    if (!loader) loader = document.getElementById('page-loader');
    return loader;
  }
  function show() {
    var el = ensureLoader();
    if (el) el.classList.add('show');
  }
  function hide() {
    var el = ensureLoader();
    if (el) el.classList.remove('show');
  }

  // Show on navigation away, hide after load
  window.addEventListener('beforeunload', show);
  window.addEventListener('load', hide);

  // fetch wrapper
  if (window.fetch) {
    var _fetch = window.fetch;
    window.fetch = function () {
      show();
      return _fetch.apply(this, arguments)
        .then(function (res) { hide(); return res; })
        .catch(function (err) { hide(); throw err; });
    };
  }

  // XHR wrapper
  (function () {
    var open = XMLHttpRequest.prototype.open;
    var send = XMLHttpRequest.prototype.send;
    var pending = 0;

    function onDone() {
      pending = Math.max(0, pending - 1);
      if (pending === 0) hide();
    }

    XMLHttpRequest.prototype.open = function () {
      return open.apply(this, arguments);
    };

    XMLHttpRequest.prototype.send = function () {
      pending += 1;
      show();
      this.addEventListener('loadend', onDone);
      return send.apply(this, arguments);
    };
  })();

  // Optional: htmx support if present
  if (window.htmx) {
    document.body.addEventListener('htmx:beforeRequest', show);
    document.body.addEventListener('htmx:afterOnLoad', hide);
    document.body.addEventListener('htmx:responseError', hide);
  }

  // Fallback: if something goes wrong, auto-hide after 10s
  setTimeout(hide, 10000);
})();
