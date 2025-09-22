Base setup of my N.N.

```python
            # Convolutional layer. Learn 32 filters using a 3x3 kernel.
            tf.keras.layers.Conv2D(
                32, (3, 3), activation="relu", input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)
            ),
            # Max-pooling layer, using 2x2 pool size
            tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
            # Second convolution layer. The second layer uses 64 filters.
            tf.keras.layers.Conv2D(64, (3, 3), activation="relu"),
            # Second max pooling layer
            tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
            # Flatten units
            tf.keras.layers.Flatten(),
            # Hidden layer with dropout
            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dropout(0.5),
            # Output layer
            tf.keras.layers.Dense(NUM_CATEGORIES, activation="softmax"),
```

Metrics of the base setup: accuracy: 0.9620 - loss: 0.1484

Different numbers of convolutional and pooling layers: In the base setup, two convolutional and max pooling processes are used. While one process is not enough, using three processes doesn't noticeably make improvements.

Dropout doesn't seem to affect accuracy much.

The # of filters for the first and second convolutional layers need to be in right size. First smaller, second larger.
