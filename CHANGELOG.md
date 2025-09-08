# Histórico de Atualizações - Gerenciador de Jogos

## [1.2.0] - 08/09/2025

### Melhorias
- ✅ **IDs centralizados**: Números de ID agora aparecem centralizados na tabela
- ✅ **Melhor alinhamento**: Preços e status também centralizados para melhor visualização
- ✅ **Interface refinada**: Ajustes visuais na tabela para melhor experiência do usuário

### Como Atualizar
1. Baixe o novo executável `GerenciadorDeJogos.exe` da pasta `dist/`
2. Substitua o arquivo antigo pelo novo
3. Seus dados serão mantidos automaticamente

---

## [1.1.0] - 31/08/2025

### Adicionado
- ✅ **Sistema de Lixeira**: Recupere jogos excluídos acidentalmente
- ✅ **Exclusão permanente**: Remova jogos definitivamente da lixeira
- ✅ **Limpeza total**: Opção para esvaziar toda a lixeira de uma vez

### Melhorias
- ✅ **Validação de preços**: Aceita múltiplos formatos (R$ 100,00, 100.00, 100,00)
- ✅ **Formatação automática**: Preços são formatados automaticamente para padrão brasileiro
- ✅ **Confirmações**: Diálogos de confirmação para ações importantes
 
---

## [1.0.0] - 31/08/2025

### Lançamento Inicial
- ✅ **Cadastro de jogos**: Adicione jogos com nome, preço e status
- ✅ **Três status**: Pago (verde), Não Pago (vermelho), Reembolsado (laranja)
- ✅ **Sistema de IDs**: Identificação única sequencial para cada jogo
- ✅ **Pesquisa em tempo real**: Encontre jogos por nome, ID ou preço
- ✅ **Edição segura**: Edite jogos com confirmação de alterações
- ✅ **Persistência automática**: Dados salvos em arquivo JSON automaticamente
- ✅ **Executável standalone**: Versão .exe que não requer Python instalado

### Funcionalidades Básicas
- ✅ Adicionar, editar e excluir jogos
- ✅ Interface com tabela organizada
- ✅ Barra de pesquisa funcional
- ✅ Menu de opções
- ✅ Salvamento automático em `games.json`

---

## 📋 Como Atualizar

### Para Usuários do Executável:
1. **Baixe a nova versão** da pasta [`dist/`](dist/)
2. **Substitua o arquivo antigo** pelo novo
3. **Seus dados são preservados** - o arquivo `games.json` não é alterado

### Para Desenvolvedores:
```bash
# Atualize o código fonte
git pull origin main

# Instale dependências se necessário
pip install PyQt5

# Execute a nova versão
python game_manager.py

# Ou gere novo executável
pyinstaller --onefile --windowed --name "GerenciadorDeJogos" game_manager.py