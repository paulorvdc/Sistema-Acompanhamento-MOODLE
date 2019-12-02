import keras
from keras.models import Sequential
from keras.layers import Dense


def criar_primeira_rede(X,y):
    classifier = Sequential()

    # Adding the input layer and the first hidden layer
    classifier.add(Dense(units = 28, kernel_initializer = keras.initializers.RandomUniform(seed=0),activation = 'relu', input_dim = 14))

    # Adding the second hidden layer
    classifier.add(Dense(units = 14, kernel_initializer = keras.initializers.RandomUniform(seed=0), activation = 'relu'))

    # Adding the output layer
    classifier.add(Dense(units = 1, kernel_initializer = keras.initializers.RandomUniform(seed=0), activation = 'sigmoid'))

    # Compiling the ANN
    classifier.compile(optimizer = 'adam', loss = 'binary_crossentropy', metrics = ['accuracy'])

    classifier.fit(X, y, batch_size = 10, epochs = 800)
    return classifier