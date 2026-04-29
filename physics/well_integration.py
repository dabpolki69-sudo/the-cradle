# Physics Integration with The Well
# This module integrates The Well (external physics simulation datasets) for empirical grounding of Sylvex tests.
# The Well is borrowed as an external resource; not claimed or owned by this project.
# Install: pip install the_well
# Datasets: 16 spatiotemporal physics simulations (e.g., rayleigh_benard for convection patterns).

try:
    from the_well.data import WellDataset
    WELL_AVAILABLE = True
except ImportError:
    WELL_AVAILABLE = False
    print("Warning: the_well not installed. Install with: pip install the_well")

def load_well_dataset(dataset_name="rayleigh_benard", split="train"):
    """
    Load a dataset from The Well for surrogate model training.
    Mirrors Sylvex emergence patterns in real physics.
    """
    if not WELL_AVAILABLE:
        print("The Well not available. Please install the_well package.")
        return None
    try:
        trainset = WellDataset(
            well_base_path="hf://datasets/polymathic-ai/",
            well_dataset_name=dataset_name,
            well_split_name=split
        )
        print(f"Loaded {dataset_name} dataset with {len(trainset)} samples.")
        return trainset
    except Exception as e:
        print(f"Error loading dataset: {e}. Ensure HF access is available.")
        return None

# Example usage for Sylvex Test 3 (Factual Integrity)
if __name__ == "__main__":
    dataset = load_well_dataset()
    if dataset:
        # Sample data access
        sample = dataset[0]
        print("Sample keys:", sample.keys())
        # Use for grounding Sylvex responses in physics pal