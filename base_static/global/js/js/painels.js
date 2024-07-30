// Defina uma função que faz uma solicitação AJAX para verificar se houve alguma alteração no modelo
function checkForUpdates() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        // Se houver uma alteração, atualize a página
        if (this.responseText == 'update') {
          location.reload();
        }
      }
    };
    xhttp.open("GET", "/check_updates/", true);
    xhttp.send();
  }
  
  // Chame a função "checkForUpdates" a cada 5 segundos
  setInterval(checkForUpdates, 5000);
  