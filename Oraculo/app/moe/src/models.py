from tensorflow.keras.layers import *
from tensorflow.keras.models import Model

class ModelBuilderExpert:
    """Builds expert models for binary classification on tabular data."""
    def __init__(self, input_shape, strategy):
        self.input_shape = input_shape
        self.strategy = strategy

    def build_mlp_residual_model(self, units=128, num_blocks=3, dropout_rate=0.2):
        with self.strategy.scope():
            def residual_block(x, units):
                shortcut = x
                x = Dense(units, activation='relu')(x)
                x = BatchNormalization()(x)
                x = Dropout(dropout_rate)(x)
                x = Dense(units, activation='relu')(x)
                x = BatchNormalization()(x)
                x = Dropout(dropout_rate)(x)
                x = Add()([shortcut, x])
                return x

            inputs = Input(shape=(self.input_shape,))
            x = Dense(units, activation='relu')(inputs)
            x = BatchNormalization()(x)
            x = Dropout(dropout_rate)(x)

            for _ in range(num_blocks):
                x = residual_block(x, units)

            outputs = Dense(1, activation='sigmoid')(x)
            return Model(inputs=inputs, outputs=outputs)

    def build_cnn_model(self, filters=32, kernel_size=3, dropout_rate=0.2):
        with self.strategy.scope():
            inputs = Input(shape=(self.input_shape,))
            x = Reshape((self.input_shape, 1))(inputs)
            x = Conv1D(filters, kernel_size, activation='relu', padding='same')(x)
            x = BatchNormalization()(x)
            x = Dropout(dropout_rate)(x)
            x = Conv1D(filters, kernel_size, activation='relu', padding='same')(x)
            x = BatchNormalization()(x)
            x = Dropout(dropout_rate)(x)
            x = Flatten()(x)
            outputs = Dense(1, activation='sigmoid')(x)
            return Model(inputs=inputs, outputs=outputs)

    def build_lstm_model(self, units=64, dropout_rate=0.2):
        with self.strategy.scope():
            inputs = Input(shape=(self.input_shape,))
            x = Reshape((self.input_shape, 1))(inputs)
            x = LSTM(units, return_sequences=True)(x)
            x = Dropout(dropout_rate)(x)
            x = LSTM(units)(x)
            x = Dropout(dropout_rate)(x)
            outputs = Dense(1, activation='sigmoid')(x)
            return Model(inputs=inputs, outputs=outputs)

    def build_attention_model(self, num_heads=4, ff_dim=64, dropout_rate=0.2):
        with self.strategy.scope():
            inputs = Input(shape=(self.input_shape,))
            x = Reshape((self.input_shape, 1))(inputs)
            attn_output = MultiHeadAttention(num_heads=num_heads, key_dim=32)(x, x)
            x = LayerNormalization(epsilon=1e-6)(x + attn_output)
            ffn = Dense(ff_dim, activation='relu')(x)
            ffn = Dense(x.shape[-1])(ffn)
            x = LayerNormalization(epsilon=1e-6)(x + Dropout(dropout_rate)(ffn))
            x = GlobalAveragePooling1D()(x)
            x = Dropout(dropout_rate)(x)
            x = Dense(ff_dim, activation='relu')(x)
            x = Dropout(dropout_rate)(x)
            outputs = Dense(1, activation='sigmoid')(x)
            return Model(inputs=inputs, outputs=outputs)
class ModelBuilderGate:
    """Builds expert models for multi-class classification on tabular data."""
    def __init__(self, input_shape, num_classes, strategy):
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.strategy = strategy

    def build_mlp_residual_model(self, units=128, num_blocks=3, dropout_rate=0.2):
        with self.strategy.scope():
            def residual_block(x, units):
                shortcut = x
                x = Dense(units, activation='relu')(x)
                x = BatchNormalization()(x)
                x = Dropout(dropout_rate)(x)
                x = Dense(units, activation='relu')(x)
                x = BatchNormalization()(x)
                x = Dropout(dropout_rate)(x)
                x = Add()([shortcut, x])
                return x

            inputs = Input(shape=(self.input_shape,))
            x = Dense(units, activation='relu')(inputs)
            x = BatchNormalization()(x)
            x = Dropout(dropout_rate)(x)

            for _ in range(num_blocks):
                x = residual_block(x, units)

            outputs = Dense(self.num_classes, activation='softmax')(x)
            return Model(inputs=inputs, outputs=outputs)

    def build_cnn_model(self, filters=64, dropout_rate=0.2):
        with self.strategy.scope():
            inputs = Input(shape=(self.input_shape,))
            x = Reshape((self.input_shape, 1))(inputs)
            x = Conv1D(filters, kernel_size=3, padding='same', activation='relu')(x)
            x = BatchNormalization()(x)
            x = Conv1D(filters, kernel_size=3, padding='same', activation='relu')(x)
            x = BatchNormalization()(x)
            x = GlobalAveragePooling1D()(x)
            x = Dense(filters, activation='relu')(x)
            x = BatchNormalization()(x)
            x = Dropout(dropout_rate)(x)
            outputs = Dense(self.num_classes, activation='softmax')(x)
            return Model(inputs=inputs, outputs=outputs)

    def build_lstm_model(self, units=64, dropout_rate=0.2):
        with self.strategy.scope():
            inputs = Input(shape=(self.input_shape,))
            x = Reshape((self.input_shape, 1))(inputs)
            x = LSTM(units, return_sequences=True)(x)
            x = Dropout(dropout_rate)(x)
            x = LSTM(units)(x)
            x = Dropout(dropout_rate)(x)
            x = Dense(units, activation='relu')(x)
            x = Dropout(dropout_rate)(x)
            outputs = Dense(self.num_classes, activation='softmax')(x)
            return Model(inputs=inputs, outputs=outputs)

    def build_attention_model(self, num_heads=4, ff_dim=64, dropout_rate=0.2):
        with self.strategy.scope():
            inputs = Input(shape=(self.input_shape,))
            x = Reshape((self.input_shape, 1))(inputs)
            attn_output = MultiHeadAttention(num_heads=num_heads, key_dim=32)(x, x)
            x = LayerNormalization(epsilon=1e-6)(x + attn_output)
            ffn = Dense(ff_dim, activation='relu')(x)
            ffn = Dense(x.shape[-1])(ffn)
            x = LayerNormalization(epsilon=1e-6)(x + Dropout(dropout_rate)(ffn))
            x = GlobalAveragePooling1D()(x)
            x = Dropout(dropout_rate)(x)
            x = Dense(ff_dim, activation='relu')(x)
            x = Dropout(dropout_rate)(x)
            outputs = Dense(self.num_classes, activation='softmax')(x)
            return Model(inputs=inputs, outputs=outputs)
