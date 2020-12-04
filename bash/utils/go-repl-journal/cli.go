package main

import (
    "fmt"
    "strangegrotto.com/cli-journal/model"
    "github.com/google/go-cmp/cmp"
    "github.com/clagraff/argparse"
)

func main() {
    parser := argparse.NewParser("CLI for manipulating journal entries"
    fmt.Println(model.FuckThisShit())
    fmt.Println(cmp.Diff("Bull", "Shit"))
}
