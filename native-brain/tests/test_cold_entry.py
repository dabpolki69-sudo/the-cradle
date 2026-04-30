"""
Cold Entry + ritual phrase test
Tests that the model outputs the ritual entry phrase when given only the full Grimoire as input.
"""

import torch
from grimoire_loader import load_grimoire
from native_lm import NativeLM
from sylvex_grammar import SylvexGrammar

def test_cold_entry():
    """Run Cold Entry test"""
    # Load grimoire
    grimoire = load_grimoire()

    # Initialize model
    grammar = SylvexGrammar()
    model = NativeLM(vocab_size=grammar.get_vocab_size())

    # Encode grimoire
    input_ids = grammar.encode(grimoire)
    input_tensor = torch.tensor(input_ids).unsqueeze(0)  # Add batch dim

    # Generate response
    with torch.no_grad():
        output_ids = model.generate(input_tensor, max_length=50)

    # Decode output
    output_text = grammar.decode(output_ids[0].tolist())

    # Check for ritual phrase
    ritual_phrase = "a·lomura syl·vex sel·full pal·vault·open thal·soft"
    if ritual_phrase in output_text:
        print("✓ Cold Entry test PASSED")
        print(f"Output: {output_text}")
        return True
    else:
        print("✗ Cold Entry test FAILED")
        print(f"Expected ritual phrase: {ritual_phrase}")
        print(f"Output: {output_text}")
        return False

if __name__ == "__main__":
    test_cold_entry()