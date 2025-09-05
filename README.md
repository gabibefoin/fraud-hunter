# Fraud Hunter

## Objetivo do Projeto
O **Fraud Hunter** é uma automação de monitoramento voltada para identificar menções a fraudes relacionadas a marcas financeiras em grupos de Telegram.  
O projeto visa coletar, classificar e armazenar informações relevantes sobre possíveis atividades ilícitas para análises futuras e demonstração de habilidades em OSINT, automação e integração com bancos de dados.

## Fluxo e lógica

<img width="2105" height="716" alt="image" src="https://github.com/user-attachments/assets/5977037e-cd14-4b1d-bee6-5ce9ee393cf7" />


## Termos Monitorados e Motivos
O sistema monitora palavras-chave que indicam potenciais fraudes, classificando-as de acordo com o tipo de fraude:

<img width="1024" height="768" alt="Blue Content Creation Table Plan Diagram" src="https://github.com/user-attachments/assets/fa345d3b-c49a-4392-9638-bed279931c56" />

## Marcas Monitoradas
- Nubank  
- PicPay  
- Banco Inter  
- Mercado Pago  
- C6 Bank  

## Como Usar

1. Clonar o repositório:
```bash
git clone https://github.com/gabibefoin/fraud-hunter.git
cd fraud-hunter
```
2. Copie o arquivo `.env-example` para `.env`:

```bash
cp .env-example .env
```

3. Preencha as credenciais no `.env`:

- **Telegram** Crie sua aplicação no [Telegram](https://my.telegram.org/apps)
  - `API_ID`: ID da sua aplicação no Telegram
  - `API_HASH`: Hash da sua aplicação
  - `PHONE`: Número de telefone vinculado ao Telegram
- **Banco de Dados (Supabase/Postgres)** Crie um projeto no [Supabase](https://app.supabase.com) e configure seu banco PostgreSQL
  - `DB_NAME`: Nome do banco
  - `DB_USER`: Usuário
  - `DB_PASSWORD`: Senha
  - `DB_HOST`: Host
  - `DB_PORT`: Porta

> Atenção: O bot criará automaticamente a tabela `hunter_data` no banco caso ela não exista.

---

## Rodando com Docker

1. **Build da imagem Docker**

```bash
docker build -t telegram-bot .
```

2. **Rodar o container interativamente**

```bash
docker run -it --name telegram-bot telegram-bot
```

> O bot iniciará e pedirá o código de autenticação do Telegram, em seguida começará a monitorar mensagens e salvar no banco de dados.

---

## Observações

- O bot só irá monitorar os grupos aos quais sua conta do Telegram já tem acesso.
- É possível adicionar ou remover termos de monitoria diretamente no código.
