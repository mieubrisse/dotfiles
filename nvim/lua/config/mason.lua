require("mason").setup()

-- attaches capabilities to ALL servers
local cmp_capabilities = require('cmp_nvim_lsp').default_capabilities()
vim.lsp.config('*', {      -- the * means “all servers”
  capabilities = cmp_capabilities,  -- you can add on_attach here too
})

-- 2. Initialize Mason-LSPConfig with my servers
require('mason-lspconfig').setup({
    ensure_installed = {
        'lua-language-server',
        'bash-langauge-server',
        'gopls',
        'marksman',
    },

    -- NOTE: this will automatically call the vim.lsp.enable commands
    -- to enable the servers
    automatic_installation = true,
})
