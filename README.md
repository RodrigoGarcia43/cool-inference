# Cool Inference

## Utilización

### Ejemplos

## Detalles

### Inferencia de tipos

La inferencia de tipos en cool se realiza en una fase posterior al chequeo
semántico. A cada nodo con un identificador se le asocia una _bolsa de tipos_,
la cuales son similares a conjuntos. Estas bolsas de tipo indican cuales son
los posibles tipos que puede tener el atributo, método o parámetro al que se
asocia la bolsa. Al comienzo de esta fase se inicializan estas bolsas de
tipos, aquellas de los nodo con `AUTO_TYPE` contiene inicialmente todos los
tipos conocidos en el programa, y la del resto de los nodos, el tipo que
aparece en la declaración del mismo. Luego se procede a _reducir_ estas
bolsas de tipo a partir de operaciones de unión e intersección entre las
bolsas, de manera tal que al final de estas reducciones se permita tomar una
decisión acerca del tipo de estos nodos.
