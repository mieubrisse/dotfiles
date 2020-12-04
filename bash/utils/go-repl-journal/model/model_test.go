package model

import "testing"

func TestFuckThisShit(t *testing.T) {
    expected_output := "Moving on"
    if MovingOn() != expected_output {
        t.Error("Expected output didn't match")
    }
}
