// Sends GoatCounter events for outbound link clicks and opened interview answers.
// Page views are counted by GoatCounter's count.js, loaded in each page.
(function () {
  function track(path, title) {
    if (window.goatcounter && window.goatcounter.count) {
      window.goatcounter.count({ path: path, title: title, event: true });
    }
  }

  document.addEventListener('click', function (e) {
    var link = e.target.closest && e.target.closest('a[href^="http"]');
    if (link && link.host !== location.host) {
      track('click: ' + link.href, link.textContent.trim());
    }
  });

  document.querySelectorAll('details[id]').forEach(function (answer) {
    answer.addEventListener('toggle', function () {
      if (answer.open) track('answer: ' + answer.id, answer.querySelector('h3') ? answer.querySelector('h3').textContent : answer.id);
    });
  });
})();
