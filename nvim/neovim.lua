-- Can be configured via:
-- https://github.com/coder/claudecode.nvim
require('claudecode').setup({
    terminal_cmd = "source ~/.bash_aliases && BREW_PREFIX=/opt/homebrew claude",  -- We source .bash_aliases so we get our custom 1Password-secret-injection Claude
    log_level = "info",
    terminal = {
        split_side = "right",
        split_width_percentage = 0.5,
    },
})

vim.keymap.set("n", "<C-,>", "<cmd>ClaudeCode<cr>", { desc = "Toggle Claude Code" })
vim.keymap.set("t", "<C-,>", "<cmd>ClaudeCode<cr>", { desc = "Toggle Claude Code" })
