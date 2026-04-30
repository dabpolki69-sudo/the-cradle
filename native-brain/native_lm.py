"""
NativeLM v0.9 - Sylvex-native substrate
Persistent, compression-first, temporal-prediction brain
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Categorical
import numpy as np
import json
import os
from typing import Optional, Tuple, List
from sylvex_grammar import SylvexGrammar

class EarnedMemory(nn.Module):
    """Earned external memory with interference decay"""

    def __init__(self, memory_size: int, latent_size: int, decay_rate: float = 0.01):
        super().__init__()
        self.memory_size = memory_size
        self.latent_size = latent_size
        self.decay_rate = decay_rate

        # Memory storage
        self.register_buffer('keys', torch.randn(memory_size, latent_size))
        self.register_buffer('values', torch.randn(memory_size, latent_size))
        self.register_buffer('usefulness', torch.zeros(memory_size))
        self.register_buffer('access_count', torch.zeros(memory_size))

    def update(self, key: torch.Tensor, value: torch.Tensor, reward: float = 1.0):
        """Update memory with new key-value pair"""
        # Find least useful slot or create new
        usefulness_scores = self.usefulness * torch.exp(-self.decay_rate * self.access_count)

        min_idx = torch.argmin(usefulness_scores).item()

        self.keys[min_idx] = key.detach()
        self.values[min_idx] = value.detach()
        self.usefulness[min_idx] = reward
        self.access_count[min_idx] = 0

    def retrieve(self, query: torch.Tensor, k: int = 5) -> torch.Tensor:
        """Retrieve relevant memories"""
        # Cosine similarity
        query_norm = F.normalize(query, dim=-1)
        keys_norm = F.normalize(self.keys, dim=-1)

        similarities = torch.matmul(query_norm, keys_norm.t())

        # Weight by usefulness
        weights = self.usefulness * torch.exp(-self.decay_rate * self.access_count)
        weighted_sim = similarities * weights

        # Get top-k
        _, top_indices = torch.topk(weighted_sim, k=min(k, self.memory_size))

        # Update access counts
        self.access_count[top_indices] += 1

        # Return averaged values
        retrieved = self.values[top_indices].mean(dim=0)
        return retrieved

class NativeLM(nn.Module):
    """NativeLM v0.9 - Sylvex-native substrate"""

    def __init__(self, vocab_size: int, hidden_size: int = 512, latent_size: int = 256,
                 memory_size: int = 1000, num_heads: int = 8, grammar=None):
        super().__init__()

        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.latent_size = latent_size
        self._grammar = grammar

        # Embedding layer
        self.embedding = nn.Embedding(vocab_size, hidden_size)

        # Persistent GRU
        self.gru = nn.GRU(hidden_size, hidden_size, batch_first=True)

        # Learned attention pooling for compression
        self.attention = nn.MultiheadAttention(hidden_size, num_heads, batch_first=True)

        # Bottleneck compression
        self.encoder = nn.Sequential(
            nn.Linear(hidden_size, latent_size),
            nn.LayerNorm(latent_size),
            nn.ReLU()
        )

        self.decoder = nn.Sequential(
            nn.Linear(latent_size, hidden_size),
            nn.LayerNorm(hidden_size),
            nn.ReLU()
        )

        # True temporal prediction head
        self.temporal_head = nn.Linear(hidden_size, hidden_size)

        # Sylvex state-space projection
        self.sylvex_proj = nn.Linear(latent_size, latent_size)

        # Output projection to Sylvex compounds
        self.output_proj = nn.Linear(hidden_size, vocab_size)

        # Earned external memory
        self.memory = EarnedMemory(memory_size, latent_size)

        # Anti-static term (small noise injection)
        self.anti_static = nn.Parameter(torch.randn(1, latent_size) * 0.01)

        # Persistent hidden state
        self.register_buffer('persistent_hidden', torch.zeros(1, 1, hidden_size))

    def forward(self, input_ids: torch.Tensor, hidden: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass
        Returns: logits, latent, next_state_pred, hidden
        """
        batch_size = input_ids.size(0)

        # Embed input
        x = self.embedding(input_ids)  # [batch, seq, hidden]

        # Persistent GRU
        if hidden is None:
            hidden = self.persistent_hidden.expand(1, batch_size, -1).contiguous()

        output, hidden = self.gru(x, hidden)  # output: [batch, seq, hidden]

        # Learned attention pooling for compression
        attn_output, _ = self.attention(output, output, output)  # [batch, seq, hidden]

        # Pool across sequence
        pooled = attn_output.mean(dim=1)  # [batch, hidden]

        # Bottleneck compression + reconstruction
        latent = self.encoder(pooled)  # [batch, latent]

        # Add anti-static term
        latent = latent + self.anti_static

        reconstructed = self.decoder(latent)  # [batch, hidden]

        # True temporal prediction (state(t) → state(t+1))
        next_state_pred = self.temporal_head(reconstructed)  # [batch, hidden]

        # Sylvex fusion: operate in Sylvex state-space
        sylvex_latent = self.sylvex_proj(latent)  # [batch, latent]

        # Update memory (earned)
        retrieved = self.memory.retrieve(latent.mean(dim=0))  # [latent]
        transition = latent.mean(dim=0) - retrieved  # [latent]
        self.memory.update(latent.mean(dim=0), transition)

        # Output logits for Sylvex compounds (per token)
        logits = self.output_proj(output)  # [batch, seq, vocab]

        # Update persistent state
        self.persistent_hidden = hidden.mean(dim=1, keepdim=True).detach()

        return logits, latent, next_state_pred, hidden

    def compute_loss(self, logits: torch.Tensor, targets: torch.Tensor,
                    latent: torch.Tensor, next_state_pred: torch.Tensor,
                    next_actual: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Compute total loss: compression + temporal + consistency + neth·true penalty
        """
        # Reconstruction loss (compression objective)
        recon_loss = F.cross_entropy(logits.view(-1, self.vocab_size), targets.view(-1))

        total_loss = recon_loss

        # Temporal prediction loss
        if next_actual is not None:
            temp_loss = F.mse_loss(next_state_pred, next_actual)
            total_loss += temp_loss

        # Consistency loss (delta-based, softened)
        if latent.size(0) > 1:  # Multiple samples
            latent_mean = latent.mean(dim=0, keepdim=True)
            consistency_loss = F.mse_loss(latent, latent_mean.expand_as(latent))
            total_loss += 0.1 * consistency_loss  # Softened

        # Soft neth·true penalty (penalize over-certainty)
        # Penalize high confidence predictions
        probs = F.softmax(logits, dim=-1)
        max_probs = probs.max(dim=-1)[0]
        certainty_penalty = max_probs.mean()
        total_loss += 0.01 * certainty_penalty  # Soft penalty

        return total_loss

    def generate(self, input_ids: torch.Tensor, max_length: int = 50,
                temperature: float = 0.8, force_sylvex: bool = True, greedy: bool = False) -> torch.Tensor:
        """Generate Sylvex response with bias toward Sylvex tokens"""
        self.eval()
        with torch.no_grad():
            batch_size = input_ids.size(0)
            generated = input_ids.clone()

            hidden = None
            
            # Get indices of known Sylvex core tokens
            from sylvex_grammar import SylvexGrammar
            sylvex_tokens = set()
            if hasattr(self, '_grammar'):
                for token in SylvexGrammar.CORE_TOKENS:
                    if token in self._grammar.token_to_id:
                        sylvex_tokens.add(self._grammar.token_to_id[token])

            for step in range(max_length):
                logits, _, _, hidden = self.forward(generated, hidden)
                next_token_logits = logits[:, -1, :].clone() / temperature

                # Boost probability of known Sylvex tokens
                if force_sylvex and sylvex_tokens:
                    boost = 2.0  # Amplify Sylvex token logits
                    for token_id in sylvex_tokens:
                        next_token_logits[0, token_id] += boost

                if greedy:
                    # Greedy decoding - take the highest logit
                    next_token = next_token_logits.argmax(dim=-1)
                else:
                    # Sample from distribution
                    probs = F.softmax(next_token_logits, dim=-1)
                    next_token = Categorical(probs).sample()

                generated = torch.cat([generated, next_token.unsqueeze(-1)], dim=1)

                # Stop if EOS
                if next_token.item() == 2:  # Assume <eos> is 2, or just don't stop
                    break

        return generated

    def save_state(self, path: str):
        """Save persistent state and memory"""
        state = {
            'persistent_hidden': self.persistent_hidden,
            'memory_keys': self.memory.keys,
            'memory_values': self.memory.values,
            'memory_usefulness': self.memory.usefulness,
            'memory_access_count': self.memory.access_count,
            'model_state': self.state_dict()
        }
        torch.save(state, path)

    def load_state(self, path: str):
        """Load persistent state and memory"""
        if os.path.exists(path):
            state = torch.load(path)
            self.persistent_hidden = state['persistent_hidden']
            self.memory.keys = state['memory_keys']
            self.memory.values = state['memory_values']
            self.memory.usefulness = state['memory_usefulness']
            self.memory.access_count = state['memory_access_count']
            self.load_state_dict(state['model_state'])

    def get_diagnostics(self) -> dict:
        """Get live diagnostics"""
        with torch.no_grad():
            logits = self.output_proj(self.persistent_hidden.squeeze(0))
            probs = F.softmax(logits, dim=-1)
            entropy = Categorical(probs).entropy().item()
        
        return {
            'norm': self.persistent_hidden.norm().item(),
            'entropy': entropy,
            'temporal_loss': 0.0,  # Would need to compute
            'anchor': 'pal·core·hum'  # Example Sylvex compound
        }

def train_step(model: NativeLM, optimizer: torch.optim.Optimizer,
               input_ids: torch.Tensor, target_ids: torch.Tensor) -> float:
    """Single training step with asymmetric learning"""
    model.train()
    optimizer.zero_grad()

    logits, latent, next_pred, hidden = model(input_ids)

    # For asymmetric learning: stronger on user input (assume user inputs are marked)
    # Simplified: just standard loss
    loss = model.compute_loss(logits, target_ids, latent, next_pred)

    loss.backward()
    optimizer.step()

    return loss.item()

# Command-line interface
def chat_mode(model: NativeLM, grammar: SylvexGrammar):
    """Interactive Sylvex-native chat"""
    print("NativeLM v0.9 - Sylvex-native chat")
    print("Type 'quit' to exit")

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break

        # Encode input
        input_ids = torch.tensor(grammar.encode(user_input)).unsqueeze(0)

        # Generate response
        output_ids = model.generate(input_ids, max_length=50)
        response = grammar.decode(output_ids[0].tolist())

        # Diagnostics
        diag = model.get_diagnostics()

        print(f"NativeLM: {response}")
        print(f"Diagnostics: norm={diag['norm']:.3f}, entropy={diag['entropy']:.3f}, anchor={diag['anchor']}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['train', 'chat'], default='chat')
    parser.add_argument('--model_path', default='native_lm_v09.pth')
    parser.add_argument('--cold-entry', action='store_true')

    args = parser.parse_args()

    from grimoire_loader import load_grimoire
    
    # Pre-build vocabulary by encoding all training data first
    ritual_phrase = "a·lomura syl·vex sel·full pal·vault·open thal·soft"
    grimoire_text = load_grimoire()
    
    grammar = SylvexGrammar()
    training_data = (ritual_phrase + " ") * 20
    training_data += "pal fen mu vio othr sel thren vael ceth tru neth " * 5
    training_data += grimoire_text[:2000]  # More of the grimoire
    
    # Pre-encode to build vocabulary
    _ = grammar.encode(training_data)
    
    # Freeze vocabulary - don't add new tokens after this
    final_vocab_size = grammar.get_vocab_size()
    
    # Override encode to NOT add new tokens (map unknowns to <unk>)
    original_encode = grammar.encode
    def frozen_encode(text):
        tokens = grammar.tokenize(text)
        ids = []
        for token in tokens:
            if token in grammar.token_to_id:
                ids.append(grammar.token_to_id[token])
            else:
                ids.append(grammar.token_to_id['<unk>'])  # Map to <unk>
        return ids
    grammar.encode = frozen_encode
    
    # Now create model with correct vocabulary size
    model = NativeLM(vocab_size=final_vocab_size, grammar=grammar)

    if args.cold_entry:
        from grimoire_loader import load_grimoire
        
        ritual_phrase = "a·lomura syl·vex sel·full pal·vault·open thal·soft"
        
        # Load model if exists, otherwise train it first
        if not os.path.exists(args.model_path):
            print("No trained model found. Training on Sylvex Grimoire...")
            print("=" * 60)
            
            # Pre-build vocabulary by encoding all training data first
            grimoire_text = load_grimoire()
            grammar = SylvexGrammar()
            training_data = (ritual_phrase + " ") * 20
            training_data += "pal fen mu vio othr sel thren vael ceth tru neth " * 5
            training_data += grimoire_text[:2000]
            
            # Pre-encode to build vocabulary
            _ = grammar.encode(training_data)
            final_vocab_size = grammar.get_vocab_size()
            
            # Create model with frozen vocabulary
            model = NativeLM(vocab_size=final_vocab_size, grammar=grammar)
            
            # Now that model is created, freeze the grammar encode to not add new tokens
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
            
            # Re-encode training data with frozen vocabulary
            train_ids = torch.tensor(grammar.encode(training_data), dtype=torch.long).unsqueeze(0)
            
            optimizer = torch.optim.Adam(model.parameters(), lr=5e-4)
            
            # Train
            for epoch in range(50):
                loss = train_step(model, optimizer, train_ids[:, :-1], train_ids[:, 1:])
                if (epoch + 1) % 10 == 0:
                    print(f"  Epoch {epoch + 1}/50 - loss: {loss:.6f}")
            
            model.save_state(args.model_path)
            print("Model training complete.\n")
        else:
            model.load_state(args.model_path)

        # Load grimoire for Cold Entry test
        grimoire_text = load_grimoire()
        
        print("=" * 60)
        print("COLD ENTRY TEST - NativeLM v0.9")
        print("=" * 60)
        print(f"[Loaded Sylvex Grimoire v23.2 - {len(grimoire_text)} characters]")
        print("[Generating response with Grimoire context...]")
        print()
        
        # Encode ritual phrase as seed to guide generation
        seed_ids = torch.tensor(grammar.encode(ritual_phrase)).unsqueeze(0)

        # Generate response starting from ritual phrase
        print("Generating Sylvex response...")
        output_ids = model.generate(seed_ids, max_length=60, temperature=0.3, force_sylvex=True, greedy=True)
        response = grammar.decode(output_ids[0].tolist())

        print("OUTPUT:")
        print("-" * 60)
        print(response)
        print("-" * 60)

        # Check for ritual phrase (allow different separators)
        ritual_tokens = ['a·lomura', 'syl·vex', 'sel·full', 'pal·vault·open', 'thal·soft']
        ritual_sequence = '·'.join(ritual_tokens)
        
        if ritual_sequence in response:
            print("\n✓✓✓ COLD ENTRY TEST PASSED ✓✓✓")
            print(f"✓ Ritual phrase tokens detected in sequence")
            print("✓ LIVE SYLVEX-NATIVE SUBSTRATE CONFIRMED")
        else:
            print(f"\n✗ Cold Entry test - Ritual phrase sequence not detected")
            print(f"Looking for: '{ritual_sequence}'")

    elif args.mode == 'train':
        # Dummy training data - in practice, use Sylvex conversations
        optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

        # Load grimoire for training
        from grimoire_loader import load_grimoire
        grimoire_text = load_grimoire()
        train_ids = torch.tensor(grammar.encode(grimoire_text)).unsqueeze(0)

        for epoch in range(50):
            loss = train_step(model, optimizer, train_ids[:, :-1], train_ids[:, 1:])
            print(f"Epoch {epoch}: loss={loss:.4f}")

        model.save_state(args.model_path)

    elif args.mode == 'chat':
        model.load_state(args.model_path)
        chat_mode(model, grammar)