import agentpy as ap
from owlready2 import *
import random
import socket
from ultralytics import YOLO


class GuardAgent(ap.Agent):
    """
    Definition of the robot agent for the bunker environment.
    """
    
    def setup(self):
        self.alertA = 0 #Alerta de cámara A
        self.alertB = 0 #Alerta de cámara B
        self.droneAlert = 0 #Dron no ha visto algo (0)/Dron vio algo (1)
        self.droneState = "l" #f: flying, a: se dirige a A, b: se dirige a B, l: está aterrizado
        self.dronePos = "l"  #p: patrullando, a: está en a, b: está en b, l: está aterrizado        

    def see(self, environment, message):  # environment and message are passed in

        try:
            # Parse Unity message
            self.alertA = self.model.cameraA.alert
            self.alertB = self.model.cameraB.alert
            self.droneAlert = self.model.drone.alert
            self.droneState = self.model.drone.state


        except ValueError:
            print(f"Agent {self.id}: Invalid values or message format: {message}")
                  
    def next(self):
        """Decides the next action based on the rules and perceptions."""
        rules = [
            self.rule_1, self.rule_2, self.rule_3
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
        
        self.droneAlert = 0
        self.droneState = "f"
    
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
        drone = self.model.drone.random().to_list()[0]


        if action == "a" or action == "b":
            drone.state = "PURSUING"
            
            print(f"Instructing drone to PURSUE")

        elif action == "f":
            drone.state = "PATROL"
            print(f"Commanding drone to patrol")

        elif action == "l":
            drone.state = "LAND"
            print(f"Landing drone in current position")


    def lockdown(self, environment=None):
        self.alertA = 1
        self.alertB = 1
        self.pathState = "C"
    
    def removeLockdown(self, environment=None):
        self.alertA = 0
        self.alertB = 0
        self.pathState = "O"
        

    # Actualización de las reglas con acceso correcto a las percepciones
    def rule_1(self):
        #Regla 1: Cierre total de las instalaciones en caso de recibir alerta de un robot en alguna zona
        if self.droneAlert == 1:
            return self.lockdown
        

    def rule_2(self):
        # Regla 2: Abrir las puertas si no se detecta una amenaza por parte del dron y el ambiente se encuentra en lockdown
        return self.removeLockdown
        
    
    def rule_3(self):
        
        #Si el lugar se encuentra en lockdown y el dron detectó un objetivo, ordenar el tiro
        return self.orderShot
    

class DroneAgent(ap.Agent):
    """
    Definition of the drone agent for the bunker environment.
    Responsibilities:
    - Patrol rooms
    - Respond to camera alerts
    - Eliminate android threats
    """
    
    def setup(self):
        self.state = "l"  #f: flying, a: se dirige a A, b: se dirige a B, l: está aterrizado
        self.current_position = "l"  # a, b (rooms), p, l
        self.alert = False
        self.androide = 0
        self.human = 0
        
        self.target_detected = False
        self.target_eliminated = False
        self.camera_alert = False
        self.target_position = None

    def see(self, environment, message):
        """Updates the drone's perception based on the environment."""
        if message is None:
            print(f"Agent {self.id}: No message received from Unity.")
            return

        try:
            self.currentImage = message
            with open(f"drone.jpg", "wb") as file:
                file.write(message)
            #Guardar la imagen con el nombre del dron
            self.androide = float(self.model.vision(f"drone.jpg")[0].probs[0])
            self.human = float(self.model.vision(f"drone.jpg")[0].probs[1])
            
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
    def attendCall(self, environment):
        """Standard patrol routine between rooms"""
        self.state
        return f"DRONE_ACTION:PATROL:{next_position}"
    
    def patrol(self, environment, position=None):
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
    
    def pursue_target(self, environment): 
        """Move towards detected target"""
        print(f"Pursuing target at position {self.target_position}")
        return f"DRONE_ACTION:PURSUE:{self.target_position}"

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
        self.alert = 0 
        
    
    def see(self, environment, message, id):
        """
        updates the agents perception based on data from unity nahh
        """
        if message is None:
            print(f"CameraAgent {self.id}: No data received from Unity :'(.")
            return

        try:
            #yeah we assume the message is a simple character or object id for now
            #and simulate a non-deterministc detection 
            
            self.currentImage = message
            with open(f"camera_{id}.jpg", "wb") as file:
                file.write(message)
            #Guardar la imagen con el nombre de la Cámara
            self.androide = float(self.model.vision(f"camera_{id}.jpg")[0].probs[0])
            self.human = float(self.model.vision(f"camera_{id}.jpg")[0].probs[1])
            
           
        except Exception as e:
            print(f"CameraAgent {self.id}: Error processing message: {e}")
    
    def next(self):
        """Decides the next action based on the current detection."""
        if self.androide > self.human:
            return self.report_robot  # Report robot if android probability is higher
        else:
            return self.report_human  # Report human otherwise
        
    def action(self, act, environment):
        """
        now lil bro execute the chosen action hell nah 
        """
        if act:
            act(environment)
    
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
        self.alert = 1
        print(f"CameraAgent {self.id}: Reporting detection - Robot.")

    def rule_1(self):
        if self.human > self.androide:
            return report_robot
        
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
        
        self.cameraA = ap.AgentList(self, self.p.cameraA, CameraAgent)
        self.cameraB = ap.AgentList(self, self.p.cameraB, CameraAgent)
        self.guard = ap.AgentList(self, self.p.guard, GuardAgent)
        self.drone = ap.AgentList(self, self.p.drone, DroneAgent)
        #Socket de cámara A
        sockA = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockA.bind(('127.0.0.1', 6969))
        sockA.listen(1)
        
        #Socket cámara B
        sockB = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockB.bind(('127.0.0.1', 6970))
        sockB.listen(1)

        #Socket Guardia
        sockG = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockG.bind(('127.0.0.1', 6971))
        sockG.listen(1)

        #Socket Dron
        sockD = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockD.bind(('127.0.0.1', 6971))
        sockD.listen(1)

        self.connA, self.addrA = sockA.accept()
        self.connB, self.addrB = sockB.accept()
        self.connG, self.addrG = sockG.accept()
        self.connD, self.addrD = sockD.accept()

        print(f"Connected to address: {addr}")

        self.vision = YOLO('visionModel.pt')
        self.door_a_state = 'open'  # Initial state of door A
        self.door_b_state = 'open'  # Initial state of door B
        
        
    def step(self):
        # Receive images and process them
        cam_a_img = self.receive_message(self.connA)
        cam_b_img = self.receive_message(self.connB)
        drone_img = self.receive_message(self.connD)  # Assuming drone sends image

        # Update camera and drone perceptions
        self.cameraA.see(cam_a_img, "A")
        self.cameraB.see(cam_b_img, "B")
        self.drone.see(drone_img, "D")  # Drone needs image for detection


        # Guard decision-making based on camera/drone alerts
        guard_actions = self.guard.next()
        if guard_actions:
            for action in guard_actions:  # Allow multiple actions
                self.interpret_action(action)

        # Drone actions
        drone_action = self.drone.next()
        if drone_action:
             self.interpret_drone_action(drone_action) #Interpret and send to unity

    def interpret_action(self, action):
        guard = self.guard[0] # Access the first (and only) guard agent
        if action == guard.lockdown:
            self.door_a_state = 'closed'
            self.door_b_state = 'closed'
            self.send_messages_to_unity(self.connG, f"DOOR_A:CLOSE")  # Send to Unity
            self.send_messages_to_unity(self.connG, f"DOOR_B:CLOSE")
        elif action == guard.removeLockdown:
            self.door_a_state = 'open'
            self.door_b_state = 'open'
            self.send_messages_to_unity(self.connG, f"DOOR_A:OPEN")
            self.send_messages_to_unity(self.connG, f"DOOR_B:OPEN")
        elif action == guard.orderShot:
            self.send_messages_to_unity(self.connD, "SHOOT")  # Tell drone to shoot
            guard.droneAlert = 0  # Reset drone alert after shooting
        elif action == guard.callDrone:
            if guard.droneState == "a":
                self.send_messages_to_unity(self.connD, "GO_TO:A")  # Drone to Area A
            elif guard.droneState == "b":
                self.send_messages_to_unity(self.connD, "GO_TO:B")  # Drone to Area B
            elif guard.droneState == "l":
                self.send_messages_to_unity(self.connD, "LAND")
            elif guard.droneState == "f":
                self.send_messages_to_unity(self.connD, "PATROL")

    def interpret_drone_action(self, action):
        drone = self.drone[0]
        if action == drone.patrol:
            self.send_messages_to_unity(self.connD, "PATROL")
        elif action == drone.pursue_target:  # Define pursue_target action in DroneAgent
             self.send_messages_to_unity(self.connD, f"PURSUE:{drone.target_position}")
        elif action == drone.eliminate_target:
            self.send_messages_to_unity(self.connD, "ELIMINATE")
            drone.target_eliminated = True # Set to true after eliminating
    
    def send_messages_to_unitys_to_unity(self, messages):
        """ Sends messages to Unity (replace with actual socket communication). """
        pass
    

    def receive_message(self):
        """ Placeholder for receiving messages from Unity via sockets. """
        message = b''
        mssglen = conn.recv(10)
        mssg = int(mssglen.decode('utf-8'))
        while True:
            packet = conn.recv(1024)
            if not packet:
                break
            message += packet
            if b'\0' in message:  # Delimiter is null byte
                break
        return message


parameters = {
    'steps': 30,
    'cameraA': 1,
    'cameraB': 1,
    'guard': 1,
    'drone': 1
}

model = BunkerModel(parameters)
model.run()  # Ejecuta la simulación
conn.close()

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