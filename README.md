# Gerenciador de Jogos

Um aplicativo desktop desenvolvido em Python com PyQt5 para gerenciar sua coleção de jogos com controle completo de status de compra e preços.

## Sobre o Desenvolvimento

Este projeto foi desenvolvido com assistência de Inteligência Artificial para a geração do código. A intervenção humana foi utilizada para:
- Correção de bugs e ajustes finos
- Validação das funcionalidades
- Testes e garantia de qualidade
- Documentação e organização do projeto

## Funcionalidades

- ✅ **Cadastro Completo**: Adicione jogos com nome, preço e status
- ✅ **Edição Segura**: Edite jogos existentes com confirmação de alterações
- ✅ **Sistema de Lixeira**: Exclua jogos com possibilidade de recuperação
- ✅ **Busca Inteligente**: Pesquise jogos por nome, ID ou preço
- ✅ **Status Visual**: Cores para status (verde=pago, vermelho=não pago, laranja=reembolsado)
- ✅ **Persistência Automática**: Dados salvos automaticamente em JSON
- ✅ **Formatação Brasileira**: Preços formatados automaticamente (R$ 123,45)

## Como Usar

### Download e Execução

1. **Baixe o Executável**:
   - Vá para a pasta `dist/`
   - Baixe o arquivo `GerenciadorDeJogos.exe`
   - Execute-o (não precisa ter Python instalado)

2. **Primeiro Uso**:
   - Ao executar, o programa criará automaticamente um arquivo `games.json`
   - Comece adicionando seus jogos clicando em "Adicionar Jogo"

### Como Adicionar Jogos

1. Clique em **"Adicionar Jogo"**
2. Preencha o nome do jogo
3. Digite o preço (apenas números - use ponto ou vírgula para decimais)
   - Exemplos: `150.50`, `200,99`, `300`
4. Selecione o status: 
   - 🟢 **Pago**: Já adquirido
   - 🔴 **Não Pago**: Na wishlist
   - 🟠 **Reembolsado**: Devolvido
5. Clique em **OK**

### Como Pesquisar

- Use a barra de pesquisa para encontrar jogos
- Funciona por: nome, ID ou valor
- A pesquisa é em tempo real

### Como Editar

1. Selecione o jogo na tabela
2. Clique em **"Editar Jogo"**
3. Faça as alterações necessárias
4. **Confirme** a edição quando solicitado

### Sistema de Lixeira

1. Ao excluir, os jogos vão para a lixeira
2. Clique em **"Lixeira"** para gerenciar
3. Na lixeira você pode:
   - 🔄 **Restaurar**: Voltar o jogo para a lista principal
   - ⚠️ **Excluir Permanentemente**: Remover definitivamente
   - 🧹 **Limpar Tudo**: Esvaziar toda a lixeira

## Para Desenvolvedores

### Pré-requisitos
- Python 3.8+
- PyQt5

### Instalação das Dependências
```bash
pip install PyQt5


## 📦 Última Atualização
Versão 1.2.0 — 08/09/2025  
Veja o [Histórico de Atualizações](CHANGELOG.md) completo.
