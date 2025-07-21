var results = [];

export function onResult(data) {
  console.log(data);

  // Update the results list
  var resultsList = document.getElementById('results-list');
  var results = resultsList.querySelectorAll('.list-row');
  if (results.length >= 5) {
    resultsList.removeChild(results[0]); // Remove the oldest result
  }
  // Append the new result
  var li = document.createElement('li');
  li.className = "list-row text-left min-w-xs";
  li.innerHTML = `
        <div class="flex items-center justify-center">
            <img class="size-6 rounded-box text-gray-200" src="${data.imageUrl ?? 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJsdWNpZGUgbHVjaWRlLWJpcmQtaWNvbiBsdWNpZGUtYmlyZCI+PHBhdGggZD0iTTE2IDdoLjAxIi8+PHBhdGggZD0iTTMuNCAxOEgxMmE4IDggMCAwIDAgOC04VjdhNCA0IDAgMCAwLTcuMjgtMi4zTDIgMjAiLz48cGF0aCBkPSJtMjAgNyAyIC41LTIgLjUiLz48cGF0aCBkPSJNMTAgMTh2MyIvPjxwYXRoIGQ9Ik0xNCAxNy43NVYyMSIvPjxwYXRoIGQ9Ik03IDE4YTYgNiAwIDAgMCAzLjg0LTEwLjYxIi8+PC9zdmc+'}"/>
        </div>
        <div>
            <div>${data.label ?? "Unknown"}</div>
            <div class="text-xs uppercase font-semibold opacity-60">Score: ${data.score?.toFixed(2) ?? 0}</div>
        </div>
    `;
  resultsList.appendChild(li);
}