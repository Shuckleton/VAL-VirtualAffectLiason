import pyttsx3

# Initialize the TTS engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
# Set properties (optional)
engine.setProperty('rate', 150)  # Speed of speech
engine.setProperty('volume', 1)  # Volume (0.0 to 1.0)
# Example: selecting a different voice
engine.setProperty('voice', voices[1].id)  # Change index based on the list


# The text you want to convert to speech
text = """
Variables in C++ is a name given to a memory location. It is the basic unit of storage in a program. 

The value stored in a variable can be changed during program execution.
A variable is only a name given to a memory location, all the operations done on the variable effects that memory location.
In C++, all the variables must be declared before use.
Rules For Declaring Variable

The name of the variable contains letters, digits, and underscores.
The name of the variable is case sensitive (ex Arr and arr both are different variables).
The name of the variable does not contain any whitespace and special characters (ex #,$,%,*, etc).
All the variable names must begin with a letter of the alphabet or an underscore(_). 
In C++, reserved keywords like float, double, and class cannot be used as variable names.
How to Declare Variables?
A typical variable declaration is of the form: 

// Declaring a single variable
type variable_name;

// Declaring multiple variables:
type variable1_name, variable2_name, variable3_name;
A variable name can consist of alphabets (both upper and lower case), numbers, and the underscore ‘_’ character. However, the name must not start with a number. 


Initialization of a variable in C++
In the above diagram,  

datatype: Type of data that can be stored in this variable. 
variable_name: Name given to the variable. 
"""

# Speak the text
engine.say(text)
engine.runAndWait()
