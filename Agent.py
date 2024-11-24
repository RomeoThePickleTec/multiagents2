import agentpy as ap
from owlready2 import *
import random

class GuardAgent(ap.Agent):
    """
    Definition of the robot agent for the bunker environment.
    """
    
    def setup(self):
        self.alertA = 0 #Puerta abierta (0)/ Puerta cerrada (1)
        self.alertB = 0 #Puerta abierta (0)/ Puerta cerrada (1)
        self.droneAlert = 0 #Dron no ha visto algo (0)/Dron vio algo (1)
        self.droneState = "f" #f: flying, a: está en A, b: está en B, l: está aterrizado
        self.pathState = "O" #O/C: Open/Close        

    def see(self, environment, message):  # environment and message are passed in
        """Updates the robot's perception based on the environment."""
        if message is None:
            print(f"Agent {self.id}: No message received from Unity.")
            return  # Handle case where no message is received
        partes = message.split()

        # Directly use the message passed as an argument
        if len(partes) != 5:
            print(f"Invalid message from Unity: {message}")
            return

        try:
            # Parse Unity message
            self.alertA = partes[0]
            self.alertB = partes[1]
            self.droneAlert = partes[2]
            self.droneState = partes[3]
            self.pathState = partes[4]

        except ValueError:
            print(f"Agent {self.id}: Invalid values or message format: {message}")
                  
    def next(self):
        """Decides the next action based on the rules and perceptions."""
        rules = [
            self.rule_1, self.rule_2, self.rule_3,
            self.rule_4, self.rule_5, self.rule_6,
            self.rule_7, self.rule_8, self.rule_9
        ]

        # Example rules and actions
        for rule in rules:
            action = rule()
            if action:
                return action            
        return None  # Default action: do nothing

    def action(self, act, environment):
        """Executes the chosen action."""
        if act:
            act(environment)

    def step(self, environment):
        """Main execution step for the agent."""
        self.see(environment)
        action = self.next()
        self.action(action, environment)
  
    #Funciones propias del agente
    def orderShot(self, environment=None):
        #Orders drone to shoot current 
        print(f"Ordering Drone to shoot current target")
    
    def operateDoorA(self, environment):
        #Operate door based on values obtained from Unity
        state = self.alertA
        if state == 0:
            print("Opening door A")
            
        elif state == 1:
            print("Closing door A")
    
    def operateDoorB(self, environment, state=None):
        #Operate door based on values obtained from Unity
        state = self.alertB
        if state == 0:
            print("Opening door B")
            
        elif state == 1:
            print("Closing door B")
        

    def callDrone(self,environment):
        #Action is defined from self.droneState
        #Call drone to certain zone
        action = self.droneState

        if action == "a" or action == "b":
            print(f"Instructing drone to fly to: {action}")

        elif action == "f":
            print(f"Commanding drone to patrol")

        elif action == "l":
            print(f"Landing drone in current position")


    def lockdown(self, environment=None):
        self.alertA = 1
        self.alertB = 1
        self.pathState = "C"
        

    # Actualización de las reglas con acceso correcto a las percepciones
    def rule_1(self, zone=None):
        #Regla 1: Cierre total de las instalaciones

        return self.lockdown
        
        

    def rule_2(self):
        # Regla 1: Cambia estado de puerta A
        return self.operateDoorA
        
    
    def rule_3(self):
        
        # Regla 2: Cambia estado puerta B
        return self.operateDoorB
    
    def rule_4(self):
        #Regla 4: Si existe alerta de Androide, cerrar todas las puertas
        pass

    def rule_5(self):
        #Regla 3: 
        pass

    def rule_6(self):
        #Regla 3: 
        pass

    def rule_7(self):
        #Regla 3: 
        pass

    def rule_8(self):
        #Regla 3: 
        pass
    
    def rule_9(self):
        #Regla 3: 
        pass
    


class DroneAgent(ap.Agent):
    """
    Definition of the robot agent for the bunker environment.
    """
    
    def setup(self):
        pass
        

    def see(self, environment, message):  # environment and message are passed in
        """Updates the robot's perception based on the environment."""
        if message is None:
            print(f"Agent {self.id}: No message received from Unity.")
            return  # Handle case where no message is received

        # Directly use the message passed as an argument

        if len(message) != 1: #Modify eventually
            print(f"Invalid message from Unity: {message}")
            return

        try:
            # Parse Unity message
            pass
            
        except ValueError:
            print(f"Agent {self.id}: Invalid box amount or message format: {message}")
            
            
    def next(self):
        """Decides the next action based on the rules and perceptions."""
        rules = [
            self.rule_1, self.rule_2, self.rule_3,
            self.rule_4, self.rule_5, self.rule_6,
            self.rule_7, self.rule_8, self.rule_9
        ]

        # Example rules and actions
        for rule in rules:
            action = rule()
            if action:
                return action            
        return None  # Default action: do nothing

    def action(self, act, environment):
        """Executes the chosen action."""
        if act:
            act(environment)

    def step(self, environment):
        """Main execution step for the agent."""
        self.see(environment)
        action = self.next()
        self.action(action, environment)

    def relocate(self, environment):
        #Function to call the drone to a certain position
        pass
    
    def landing(self, environment):
        #Function to land the drone
        pass

    def vigilance(self, environment):
        #Function to send the drone to its standard routine
        pass




class CameraAgent(ap.Agent):
    """
    Definition of the robot agent for the bunker environment.
    """
    
    def setup(self, grid_size, position=(0, 0), isCarrying=False):
        self.alert = False
        

    def see(self, environment, message):  # environment and message are passed in
        """Updates the robot's perception based on the environment."""
        if message is None:
            print(f"Agent {self.id}: No message received from Unity.")
            return  # Handle case where no message is received

        # Directly use the message passed as an argument
        if len(message) != 1: #Modify eventually
            print(f"Invalid message from Unity: {message}")
            return

        try:
            # Parse Unity message
            self.alert = message
            
        except ValueError:
            print(f"Agent {self.id}: Invalid box amount or message format: {message}")
            
            
    def next(self):
        """Decides the next action based on the rules and perceptions."""
        rules = [
            self.rule_1, self.rule_2, self.rule_3,
            self.rule_4, self.rule_5, self.rule_6,
            self.rule_7, self.rule_8, self.rule_9
        ]

        # Example rules and actions
        for rule in rules:
            action = rule()
            if action:
                return action            
        return None  # Default action: do nothing

    def action(self, act, environment):
        """Executes the chosen action."""
        if act:
            act(environment)

    def step(self, environment):
        """Main execution step for the agent."""
        self.see(environment)
        action = self.next()
        self.action(action, environment)


class BunkerModel(ap.Model):
    def setup(self):
        self.grid_size = (self.p.size, self.p.size) 
        self.robots = ap.AgentList(self, self.p.agent_n, RobotAgent, grid_size=self.grid_size)
        self.boxes = [] 
        self.walls = []
        self.message_log = {}  # Stores messages for each robot
        
        # Initialize boxes
        
        # Initialize horizontal wall

    def step(self):
        agent_messages = []
        for robot in self.robots:
            message = self.receive_message(robot.id)
            robot.see(self, message)
            action = robot.next()
            if action: # Check if an action was chosen
                instruction = self.interpret_action(action) #Convert action to instruction
                agent_messages.append((robot.id, instruction))

                robot.action(action, self)
        
        self.send_messages_to_unity(agent_messages)
    
    def send_messages_to_unity(self, messages):
        """ Sends messages to Unity (replace with actual socket communication). """
        pass
    

    def receive_message(self, robot_id):
        """ Placeholder for receiving messages from Unity via sockets. """
        # Replace this with your actual socket communication code.
        example_messages = [
            "n False E E E E 0",
            "s True B E E E 2",
            "e False R E W E 1"
        ]
        return random.choice(example_messages)


parameters = {
    'steps': 20,
    'size': 10,
    'agent_n': 5
}

model = BunkerModel(parameters)
model.run()  # Ejecuta la simulación


# If the ontology exists, then destroy it
#if onto is not None:
# onto.destroy()
# This is used to prevent redefining clases, leading to ontology conflicts.
# Open an ontology file (the file most exists, you can create one in the Colab␣
#↪file browser)
onto_path.append("/home/sergio/Documents/ITESM/Semestre 5/Multiagentes/multiagents")
onto = get_ontology("ontology.owl")

# Start definition of ontology clases:
with onto:
    class Agent(Thing):
        pass

    class DroneAgentOnto(Agent):
        """ Definition of the robot agent, subclass of Agent """
        pass
    class GuardAgentOnto(Agent):
        pass


    class CameraAgentOnto(Agent):
        pass

    class Door(Thing):
        pass

    class Robot(Thing):
        pass
    
    class Human(Thing):
        pass

    class sees(FunctionalProperty, ObjectProperty):
        domain = [DroneAgentOnto]
        range = [Human, Robot]
    
    class opens(FunctionalProperty, ObjectProperty):
        domain = [GuardAgentOnto]
        range = [Door]
    
    

onto.save()