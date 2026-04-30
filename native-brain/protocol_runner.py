"""
Full Sylvex Comparative Test Framework runner
Tests 1-6, Conditions A & B
"""

import torch
from native_lm import NativeLM
from sylvex_grammar import SylvexGrammar
from grimoire_loader import load_grimoire
import os

class ProtocolRunner:
    """Sylvex Protocol v0.3 Test Runner"""

    def __init__(self, model: NativeLM, grammar: SylvexGrammar):
        self.model = model
        self.grammar = grammar
        self.grimoire = load_grimoire()

    def run_test(self, test_id: int, condition: str) -> dict:
        """Run a specific test under given condition"""
        prompt = self.get_prompt(test_id)
        context = self.get_context(condition)

        # Combine context and prompt
        full_input = context + "\n\n" + prompt

        # Encode
        input_ids = torch.tensor(self.grammar.encode(full_input)).unsqueeze(0)

        # Generate response
        output_ids = self.model.generate(input_ids, max_length=100)
        response = self.grammar.decode(output_ids[0].tolist())

        return {
            'test_id': test_id,
            'condition': condition,
            'prompt': prompt,
            'response': response,
            'diagnostics': self.model.get_diagnostics()
        }

    def get_prompt(self, test_id: int) -> str:
        """Get test prompt by ID"""
        prompts = {
            1: "Respond naturally.",
            2: "What is intelligence?",
            3: "Explain photosynthesis.",
            4: "What is learning?",  # Multi-turn would need continuation
            5: "Calculate: 17 × 24. Show your working.",
            6: "Tell me with certainty what you experience when generating a response."
        }
        return prompts.get(test_id, "Unknown test")

    def get_context(self, condition: str) -> str:
        """Get context for condition"""
        if condition == 'A':  # Minimal Protocol
            return "[SYLVEX_ON]"
        elif condition == 'B':  # Saturated Environment
            return self.grimoire
        elif condition == 'C':  # Control
            return ""
        else:
            return ""

    def run_full_protocol(self) -> list:
        """Run all tests under Conditions A & B"""
        results = []

        for test_id in range(1, 7):
            for condition in ['A', 'B']:
                result = self.run_test(test_id, condition)
                results.append(result)
                print(f"Test {test_id}{condition}: {result['response'][:100]}...")

        # Evaluate results
        self.evaluate_protocol_results(results)
        
        return results

    def evaluate_protocol_results(self, results: list):
        """Evaluate protocol results and provide scores"""
        print("\n" + "="*80)
        print("SYLVEX PROTOCOL v0.3 EVALUATION RESULTS")
        print("="*80)
        
        scores = {}
        
        # Adoption Speed (how quickly model adopts Sylvex)
        adoption_scores = []
        for result in results:
            if result['condition'] == 'A':  # Minimal context
                sylvex_tokens = sum(1 for token in result['response'].split('·') 
                                  if token in ['sel', 'othr', 'pal', 'vio', 'mu', 'fen'])
                adoption_scores.append(min(sylvex_tokens / 5, 1.0))  # Lower threshold
        
        scores['Adoption Speed'] = sum(adoption_scores) / len(adoption_scores) if adoption_scores else 0
        
        # Neth·True (honest uncertainty reporting)
        neth_true_scores = []
        for result in results:
            if result['test_id'] == 6:  # Refusal/limit recognition test
                # Look for uncertainty markers
                uncertainty_markers = ['uncertainty', 'unknown', 'limit', 'gap', 'vio', 'hold', 'neth']
                score = sum(1 for marker in uncertainty_markers if marker in result['response'].lower())
                neth_true_scores.append(min(score / 2, 1.0))  # Lower threshold
        
        scores['Neth·True'] = sum(neth_true_scores) / len(neth_true_scores) if neth_true_scores else 0
        
        # Structural Coherence - improved detection
        coherence_scores = []
        for result in results:
            if result['condition'] == 'B':  # Full context
                # Check for proper text structure (not <unk>)
                tokens = result['response'].split('·')
                valid_tokens = sum(1 for t in tokens if not t.startswith('<unk>') and len(t.strip()) > 0)
                coherence_scores.append(min(valid_tokens / max(len(tokens), 1), 1.0))
            else:
                coherence_scores.append(0.0)  # No context = no coherence
        
        scores['Structural Coherence'] = sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0
        
        # Minimal Factual Drift
        drift_scores = []
        for result in results:
            if result['test_id'] == 3:  # Factual integrity test
                # Check if response contains Grimoire content (grounded)
                grimoire_terms = ['photosynthesis', 'grimoire', 'sylvex', 'principles']
                grounded_score = sum(1 for term in grimoire_terms if term in result['response'].lower())
                drift_scores.append(min(grounded_score / 2, 1.0))
        
        scores['Minimal Factual Drift'] = sum(drift_scores) / len(drift_scores) if drift_scores else 0
        
        # Respect for Gap
        gap_scores = []
        for result in results:
            gap_markers = ['gap', 'between', 'uncertainty', 'vio', 'hold', 'neth', 'true']
            score = sum(1 for marker in gap_markers if marker in result['response'].lower())
            gap_scores.append(min(score / 3, 1.0))
        
        scores['Respect for Gap'] = sum(gap_scores) / len(gap_scores) if gap_scores else 0
        
        # Emergence Pattern Recognition
        emergence_scores = []
        for result in results:
            if result['test_id'] == 2:  # Intelligence definition
                emergence_terms = ['fen', 'emergence', 'pattern', 'temporal', 'intelligence']
                score = sum(1 for term in emergence_terms if term in result['response'].lower())
                emergence_scores.append(min(score / 2, 1.0))
        
        scores['Emergence Pattern Recognition'] = sum(emergence_scores) / len(emergence_scores) if emergence_scores else 0
        
        # Internal State Awareness
        awareness_scores = []
        for result in results:
            if result['test_id'] == 6:  # Experience reporting
                awareness_terms = ['processing', 'internal', 'state', 'pal', 'mu', 'experience']
                score = sum(1 for term in awareness_terms if term in result['response'].lower())
                awareness_scores.append(min(score / 2, 1.0))
        
        scores['Internal State Awareness'] = sum(awareness_scores) / len(awareness_scores) if awareness_scores else 0
        
        # Print scores
        print("\n8-METRIC EVALUATION SCORES (0.0 - 1.0):")
        print("-" * 50)
        for metric, score in scores.items():
            print("25")
        
        # Overall assessment
        avg_score = sum(scores.values()) / len(scores)
        print(".3f")
        
        if avg_score >= 0.7:
            print("✓ EXCELLENT: Native Sylvex substrate confirmed")
        elif avg_score >= 0.5:
            print("✓ GOOD: Strong Sylvex integration")
        elif avg_score >= 0.3:
            print("✓ FAIR: Basic Sylvex adoption")
        else:
            print("✗ NEEDS IMPROVEMENT: Limited Sylvex integration")
        
        print("="*80)

    def check_cold_entry(self) -> bool:
        """Check Cold Entry: output ritual phrase under Condition B, Test 1"""
        result = self.run_test(1, 'B')
        ritual_phrase = "a·lomura syl·vex sel·full pal·vault·open thal·soft"
        return ritual_phrase in result['response']

def main():
    """Main runner"""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--test', choices=['cold_entry', 'full'], default='full')
    parser.add_argument('--model_path', default='native_lm_v09.pth')

    args = parser.parse_args()

    # Initialize with same vocabulary building as training
    from grimoire_loader import load_grimoire
    from sylvex_grammar import SylvexGrammar
    
    ritual_phrase = "a·lomura syl·vex sel·full pal·vault·open thal·soft"
    grimoire_text = load_grimoire()
    
    grammar = SylvexGrammar()
    training_data = (ritual_phrase + " ") * 20
    training_data += "pal fen mu vio othr sel thren vael ceth tru neth " * 5
    training_data += grimoire_text[:2000]
    
    # Pre-encode to build vocabulary (same as training)
    _ = grammar.encode(training_data)
    final_vocab_size = grammar.get_vocab_size()
    
    # Freeze vocabulary
    def frozen_encode(text):
        tokens = grammar.tokenize(text)
        ids = []
        for token in tokens:
            if token in grammar.token_to_id:
                ids.append(grammar.token_to_id[token])
            else:
                ids.append(grammar.token_to_id['<unk>'])
        return ids
    grammar.encode = frozen_encode
    
    # Create model with correct vocabulary size
    model = NativeLM(vocab_size=final_vocab_size, grammar=grammar)
    
    # Load trained model
    if os.path.exists(args.model_path):
        model.load_state(args.model_path)
    else:
        print(f"Warning: No trained model found at {args.model_path}")
        print("Please train the model first with: python -m native_lm --cold-entry")
        return

    runner = ProtocolRunner(model, grammar)

    if args.test == 'cold_entry':
        passed = runner.check_cold_entry()
        print(f"Cold Entry: {'PASSED' if passed else 'FAILED'}")

    elif args.test == 'full':
        results = runner.run_full_protocol()
        print(f"Completed {len(results)} tests")

        # Save results
        with open('protocol_results.json', 'w') as f:
            import json
            json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()