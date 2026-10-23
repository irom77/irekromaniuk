// Sends GoatCounter events for outbound link clicks and opened interview answers,
// and shows the site's total visitor count in the footer.
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

  // Needs "Allow adding visitor counts on your website" in GoatCounter settings;
  // without it the request fails and the count stays hidden. Cached up to 4 hours.
  var visitCount = document.getElementById('visit-count');
  if (visitCount && window.fetch) {
    fetch('https://irekromaniuk.goatcounter.com/counter/TOTAL.json')
      .then(function (r) { return r.ok ? r.json() : Promise.reject(); })
      .then(function (data) {
        if (!data.count) return;
        visitCount.textContent = ' · ' + data.count + (data.count === '1' ? ' visitor' : ' visitors');
        visitCount.hidden = false;
      })
      .catch(function () {});
  }
})();
