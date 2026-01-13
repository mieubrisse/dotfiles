-- Can be configured via:
-- https://github.com/greggh/claude-code.nvim/tree/275c47615f4424a0329290ce1d0c18a8320fd8b0?tab=readme-ov-file#configuration
require('claude-code').setup({
    window = {
        split_ratio = 0.5,
        position = "vertical",
    },
    command = "source ~/.bash_aliases && BREW_PREFIX=/opt/homebrew claude"  -- We source .bash_aliases so we get our custom 1Password-secret-injection Claude
})
