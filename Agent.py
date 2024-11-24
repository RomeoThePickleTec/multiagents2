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
    Definition of the drone agent for the bunker environment.
    Responsibilities:
    - Patrol rooms
    - Respond to camera alerts
    - Eliminate android threats
    """
    
    def setup(self):
        self.state = "PATROL"  # PATROL, PURSUING, ELIMINATING
        self.current_position = "A"  # A, B (rooms)
        self.target_detected = False
        self.target_position = None
        self.target_eliminated = False
        self.camera_alert = False

    def see(self, environment, message):
        """Updates the drone's perception based on the environment."""
        if message is None:
            print(f"Agent {self.id}: No message received from Unity.")
            return

        # Message format expected: "STATE:POSITION:TARGET:CAMERA_ALERT"
        # Example: "PATROL:A:0:0" - Patrolling in room A, no target, no camera alert
        parts = message.split(":")

        if len(parts) != 4:
            print(f"Invalid message from Unity: {message}")
            return

        try:
            self.state = parts[0]
            self.current_position = parts[1]
            self.target_detected = bool(int(parts[2]))
            self.camera_alert = bool(int(parts[3]))
            
        except ValueError:
            print(f"Agent {self.id}: Invalid values or message format: {message}")
    
    def next(self):
        """Decides the next action based on the rules and perceptions."""
        rules = [
            self.patrol_rule,
            self.camera_alert_rule,
            self.target_elimination_rule,
            self.target_pursuit_rule,
            self.return_to_patrol_rule
        ]

        for rule in rules:
            action = rule()
            if action:
                return action            
        return None

    def action(self, act, environment):
        """Executes the chosen action."""
        if act:
            act(environment)

    def step(self, environment):
        """Main execution step for the agent."""
        self.see(environment)
        action = self.next()
        self.action(action, environment)

    # Acciones del dron
    def patrol(self, environment):
        """Standard patrol routine between rooms"""
        next_position = "B" if self.current_position == "A" else "A"
        print(f"Patrolling: Moving to room {next_position}")
        return f"DRONE_ACTION:PATROL:{next_position}"
    
    def pursue_target(self, environment, position=None):
        """Move towards detected target"""
        target_pos = position if position else self.target_position
        print(f"Pursuing target at position {target_pos}")
        return f"DRONE_ACTION:PURSUE:{target_pos}"

    def eliminate_target(self, environment):
        """Eliminate confirmed android target"""
        print("Eliminating android target")
        return "DRONE_ACTION:ELIMINATE"

    def recalculate_position(self, environment):
        """Recalculate position when target moves to different area"""
        print("Recalculating position to intercept target")
        return "DRONE_ACTION:RECALCULATE"

    # Reglas del dron
    def patrol_rule(self):
        """Rule: Si no hay alertas, continúa patrullando los cuartos"""
        if (self.state == "PATROL" and 
            not self.target_detected and 
            not self.camera_alert):
            return self.patrol
        return None

    def camera_alert_rule(self):
        """Rule: Si recibe una alerta de la cámara, cancelar patrullaje y moverse al objetivo detectado"""
        if self.camera_alert and self.state != "PURSUING":
            self.state = "PURSUING"
            return self.pursue_target
        return None

    def target_elimination_rule(self):
        """Rule: Si se confirma que el objetivo es un androide, eliminarlo y enviar confirmación"""
        if (self.state == "PURSUING" and 
            self.target_detected and 
            not self.target_eliminated):
            return self.eliminate_target
        return None

    def target_pursuit_rule(self):
        """Rule: Si se detecta que el androide ya cruzó al siguiente pasillo, recalcular posición"""
        if (self.state == "PURSUING" and 
            self.target_detected and 
            self.current_position != self.target_position):
            return self.recalculate_position
        return None

    def return_to_patrol_rule(self):
        """Rule: Si el androide es eliminado, volver al patrullaje"""
        if self.target_eliminated and self.state != "PATROL":
            self.state = "PATROL"
            self.target_detected = False
            self.target_eliminated = False
            self.camera_alert = False
            return self.patrol
        return None


class CameraAgent(ap.Agent):
    """
    Definition of the robot agent for the bunker environment.
    """
    
    def setup(self):
        """
        we init with the properties of the camera agent's lol
        """
        self.current_detection = None #the last detection result: 0 for human, 1 for nigga Robot
        self.environment = None #this is the placeholder for unity environment connection
    
    def perceive(self, environment, message):
        """
        updates the agents perception based on data from unity nahh
        """
        if message is None:
            print(f"CameraAgent {self.id}: No data received from Unity :'(.")
            return

        try:
            #yeah we assume the message is a simple character or object id for now
            #and simulate a non-deterministc detection 
            detection_result = random.choice([0, 1])
            if random.random() < 0.1: #here we simulates a 10% chance of error (for fun)
                detection_result = 1 - detection_result
            self.current_detection = detection_result
            print(f"CameraAgent {self.id}: Detected {'Human' if detection_result == 0 else 'Robot'}.")
        except Exception as e:
            print(f"CameraAgent {self.id}: Error processing message: {e}")
    
    def decide(self):
        """
        well, here our lil bro decide what to do based on the current detection
        """
        if self.current_detection is None:
            return None

        if self.current_detection == 0:
            return self.report_human
        else:
            return self.report_robot
        
    def act(self, action, environment):
        """
        now lil bro execute the chosen action hell nah 
        """
        if action:
            action(environment)
    
    def step(self, environment):
        """
        the main execution step for the lil cameraMan
        """
        #our lil spy simulate receiving a message (here we need replace with unity communication later)
        simulated_message = "character_data" #placeholder for the actual unity message
        self.perceive(environment, simulated_message)

        #lil bro decide and act based on perception
        action = self.decide()
        self.act(action, environment)
    
    #these are the cameraMan-specific actions
    def report_human(self, environment = None):
        """
        lil spy report detection of a Human
        """
        print(f"CameraAgent {self.id}: Reporting detection - Human.")
    
    def report_robot(self, environment = None):
        """
        lil bro report detection of a Human
        """
        print(f"CameraAgent {self.id}: Reporting detection - Robot.")

    # """
    # Definition of the robot agent for the bunker environment.
    # """
    
    # def setup(self, grid_size, position=(0, 0), isCarrying=False):
    #     self.alert = False
        

    # def see(self, environment, message):  # environment and message are passed in
    #     """Updates the robot's perception based on the environment."""
    #     if message is None:
    #         print(f"Agent {self.id}: No message received from Unity.")
    #         return  # Handle case where no message is received

    #     # Directly use the message passed as an argument
    #     if len(message) != 1: #Modify eventually
    #         print(f"Invalid message from Unity: {message}")
    #         return

    #     try:
    #         # Parse Unity message
    #         self.alert = message
            
    #     except ValueError:
    #         print(f"Agent {self.id}: Invalid box amount or message format: {message}")
            
            
    # def next(self):
    #     """Decides the next action based on the rules and perceptions."""
    #     rules = [
    #         self.rule_1, self.rule_2, self.rule_3,
    #         self.rule_4, self.rule_5, self.rule_6,
    #         self.rule_7, self.rule_8, self.rule_9
    #     ]

    #     # Example rules and actions
    #     for rule in rules:
    #         action = rule()
    #         if action:
    #             return action            
    #     return None  # Default action: do nothing

    # def action(self, act, environment):
    #     """Executes the chosen action."""
    #     if act:
    #         act(environment)

    # def step(self, environment):
    #     """Main execution step for the agent."""
    #     self.see(environment)
    #     action = self.next()
    #     self.action(action, environment)


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