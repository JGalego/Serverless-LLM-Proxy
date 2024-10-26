"""
Adapted from
https://cookbook.openai.com/examples/visualizing_embeddings_in_2d
"""

import numpy as np
import matplotlib.pyplot as plt

from sklearn.manifold import TSNE

# Load the embeddings
data = np.genfromtxt("hello_world.csv", delimiter=',')

# Create a tSNE model and transform the data
tsne = TSNE(
    n_components=2,
    perplexity=15,
    random_state=42,
    init='random',
    learning_rate=200
)
viz = tsne.fit_transform(data)

# Plot the 2D projections
plt.title("Hello World in 74 Languages")
plt.scatter(viz[:,0], viz[:,1])
plt.show()
