# Sawtooth Water Grant

Sawtooth Water Grant é um protótipo funcional de uma aplicação distribuída de gestão de outorgas de recursos hídricos. Provem o cadastro de sensores com funcionalidade IoT, que permitem que outorgados enviam automaticamente seus dados de consumo à Agência Nacional de Águas (ANA). 

Sawtooth Water Grant é construído sobre o Hyperledger Sawtooth, uma plataforma de blockchain empresarial inicialmente criada pela Hyperledger Foundation e Intel, e hoje mantida pela Splinter. Para saber mais sobre o Hyperledger Sawtooth, consulte o [repositório sawtooth-core](https://github.com/splintercommunity/sawtooth-core) e a [documentação do Hyperledger Sawtooth](https://sawtooth.splinter.dev/docs/1.2/)

Os componentes do Water Grant neste repositório incluem:

  - Um transaction processor que lida com a lógica de transações do Water Grant

  - Uma API REST personalizada que fornece endpoints HTTP/JSON para consultar dados da blockchain, criar batches e transações, e gerenciar informações de usuários

  - Um event subscriber que interpreta eventos da blockchain e armazena dados em um banco de dados auxiliar fora da blockchain

  - Dois aplicativos web cliente: Sprinkle App, que usa o Water Grant para rastrear o consumo por outorgado e gerenciar cadastros na rede, e o Audit App, que decodifica registros da blockchain para eventuais auditorias.

## Uso


Clone o repositório do Water Grant e certifique-se de que os comandos `docker` e `docker-compose` estão instalados na sua máquina.

Para executar a aplicação, navegue até o diretório raiz do projeto e use o seguinte comando:

```bash
docker-compose up
```
ou
```bash
docker compose up
```

Este comando inicia todos os componentes do Water Grant em contêineres separados.

Os endpoints HTTP disponíveis são:
- Sprinkle App: **http://localhost:8040**
- Audit App: **http://localhost:5000**
- Water Grant REST API: **http://localhost:8000**
- PostgreSQL Adminer: **http://localhost:8080**
- Sawtooth REST API: **http://localhost:8008**
