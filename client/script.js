async function obterResposta(pergunta) {
  try {
    const url = "http://localhost:55555/response?pergunta=" + encodeURIComponent(pergunta);
    const resposta = await fetch(url);
    const dados = await resposta.json();
    console.log("Resposta do servidor:", dados.resposta);
  } catch (erro) {
    console.error("Erro ao buscar resposta:", erro);
  }
}

obterResposta("Quem é Chiquinho?");
