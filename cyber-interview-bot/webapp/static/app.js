let currentQuestion = null

function el(id){ return document.getElementById(id) }
function appendChat(sender, html){
  const chat = el('chat')
  const div = document.createElement('div')
  div.className = sender === 'bot' ? 'mb-2 bot-msg' : 'mb-2 user-msg text-end'
  div.innerHTML = html
  chat.appendChild(div)
  chat.scrollTop = chat.scrollHeight
}

async function getQuestion(){
  const difficulty = el('difficulty').value
  const qtype = el('qtype').value
  const url = new URL('/api/question', window.location.origin)
  url.searchParams.set('difficulty', difficulty)
  if(qtype) url.searchParams.set('type', qtype)
  const res = await fetch(url)
  const q = await res.json()
  currentQuestion = q
  appendChat('bot', `<strong>Q (${q.difficulty} / ${q.type}):</strong> ${q.question}`)
  el('answerInput').value = ''
}

async function submitAnswer(){
  if(!currentQuestion){ alert('Get a question first.'); return }
  const answer = el('answerInput').value.trim()
  appendChat('user', `<div><strong>Your answer:</strong><pre>${escapeHtml(answer)}</pre></div>`)
  const res = await fetch('/api/evaluate', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({question_id: currentQuestion.id, answer})
  })
  const data = await res.json()
  appendChat('bot', formatFeedback(data))
  // show tips in side panel
  updateTips(data.tips)
}

function formatFeedback(data){
  let html = `<div><strong>Score:</strong> ${data.score}/10</div>`
  if(data.reason) html += `<div class="small text-muted">${escapeHtml(data.reason)}</div>`
  if(data.strengths && data.strengths.length){ html += `<div><strong>Strengths:</strong><ul>` + data.strengths.map(s=>`<li>${escapeHtml(s)}</li>`).join('') + `</ul></div>` }
  if(data.weaknesses && data.weaknesses.length){ html += `<div><strong>Areas:</strong><ul>` + data.weaknesses.map(s=>`<li>${escapeHtml(s)}</li>`).join('') + `</ul></div>` }
  if(data.tips && data.tips.length){ html += `<div><strong>Tips:</strong><ul>` + data.tips.map(s=>`<li>${escapeHtml(s)}</li>`).join('') + `</ul></div>` }
  return html
}

function updateTips(tips){
  const list = el('tipsList')
  list.innerHTML = ''
  if(tips && tips.length){
    tips.forEach(t=>{ const li = document.createElement('li'); li.textContent = t; list.appendChild(li) })
  }
}

async function explain(){
  if(!currentQuestion) return alert('Get a question first')
  const url = new URL('/api/explain', window.location.origin)
  url.searchParams.set('question_id', currentQuestion.id)
  const res = await fetch(url)
  const data = await res.json()
  appendChat('bot', `<div><strong>Explanation:</strong><div>${escapeHtml(data.explanation)}</div><div class="small text-muted">References: ${data.references.join(', ')}</div></div>`)
}

function escapeHtml(s){
  if(!s) return ''
  return s.replace(/[&<>"']/g, c=>({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":"&#39;"
  }[c]))
}

el('nextQ').addEventListener('click', getQuestion)
el('submitAns').addEventListener('click', submitAnswer)
el('explainBtn').addEventListener('click', explain)
el('skipBtn').addEventListener('click', ()=>{ appendChat('user', '<em>Skipped question</em>'); updateTips([]); currentQuestion = null })

// load first question on open
window.addEventListener('load', ()=>{ getQuestion() })
