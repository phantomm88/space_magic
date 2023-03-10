import numpy as np

# we can have the function return transformed matrix along with the coordinate system it's attached to

class ref_frame:
  # name may be any string
  def __init__(self, name='I'):
    self.name = name
  
  def __str__(self):
    return f"Reference Frame: {self.name}"
  
  def get_name(self):
    return self.name
  
class dcm:
  # supresses numpy display of scientific notation
  np.set_printoptions(suppress=True)
  
  # Parameters: ----------------
  # ref_to and ref_from are ref_frame objects
  # euler_angles is a list containing the theta_1, theta_2, and theta_3 Euler angles
  # seq is a three-character string of the numbers 1,2,3 in the desired Euler sequence
  # matrix is a parameter used if the dcm is explicitly specified, accepts numpy array
  def __init__(self, ref_to, ref_from, euler_angles=[0, 0, 0], seq='321', matrix=None):
    self.ref_to = ref_to
    self.ref_from = ref_from
    self.rot_mats = []

    if bool(np.any(matrix)):
      self.matrix = matrix
    
    else:
      order = [*seq]
      self.seq = order
      prod = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
      for i in range(0, 3):
        choice = int(order[i])
        angle = euler_angles[i]
        if choice == 1:
          temp = np.array([[1, 0, 0], [0, np.cos(angle), np.sin(angle)], [0, -np.sin(angle), np.cos(angle)]])
        elif choice == 2:
          temp = np.array([[np.cos(angle), 0, -np.sin(angle)], [0, 1, 0], [np.sin(angle), 0, np.cos(angle)]])
        else:
          temp = np.array([[np.cos(angle), np.sin(angle), 0], [-np.sin(angle), np.cos(angle), 0], [0, 0, 1]])
        
        self.rot_mats.append(temp)
        prod = np.matmul(temp, prod)
    
      self.matrix = prod

  def __str__(self):
    return f"DCM from {self.ref_from.name} --> {self.ref_to.name} (C{self.ref_from.name} = {self.ref_to.name}) with matrix \n{self.matrix}"
  
  # Purpose: -------------------------
  # Accessor method for the DCM matrix
  def get_matrix(self):
    return self.matrix
  
  # Purpose: -------------------------
  # Accessor method for the original reference frame object
  def get_ref_to(self):
    return self.ref_to
  
  # Purpose: -------------------------
  # Accessor method for the new reference frame object
  def get_ref_from(self):
    return self.ref_from
  
  # Purpose: -------------------------
  # Computes the inverse of the DCM
  # Returns: -------------------------
  # DCM object corresponding to the inverse
  def inverse(self):
    return dcm(self.ref_from, self.ref_to, matrix=self.matrix.T)    

class v:
  # ref is a ref_frame object
  # value is a numpy array
  def __init__(self, ref, value):
    self.ref = ref
    self.value = value
  
  def __str__(self):
    return f"Vector in {self.ref} with components\n{self.value}"
  
  def mag(self):
    return np.sqrt(np.dot(self.value, self.value))
  
  # Parameters: -----------------------
  # ref_to is a ref_frame object
  # dcm is a dcm object from the original ref_frame to the new ref_frame
  # Purpose: --------------------------
  # Transforms a vector from one reference frame to another
  # Returns: --------------------------
  # v object with the transformed values in the appropriate ref_frame
  def transform(self, ref_to, dcm):
    if dcm.get_ref_to() != ref_to or dcm.get_ref_from() != self.ref:
      raise Exception(f"Direct Cosine Matrix must be from reference frame {self.ref} to reference frame {ref_to}")
    return v(ref_to, np.matmul(dcm.get_matrix(), self.value))
  
  # vector on which this function acts must be theta dot
  def f_kinematics(self, dcm): 
    ref_frames = [ref_frame(), ref_frame('Intermediate'), ref_frame('Body')]
    sum = 0
    for i in range(0, 3):
      temp2 = np.zeros((3, 1))
      temp2[int(dcm.seq[i]) - 1][0] = self.value[i][0]
      if i == 0:
        mat1 = dcm.rot_mats[2] @ dcm.rot_mats[1]
      elif i == 1:
        mat1 = dcm.rot_mats[2]
      else:
        mat1 = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
      sum += mat1 @ temp2
    return v(dcm.get_ref_to(), sum)
  
  def t_theorem(self, dcm, v_dot, theta_dot):
    ang_vel = theta_dot.f_kinematics(dcm).value
    val1 = v_dot.value + np.cross(ang_vel, self.value)
    return v(dcm.get_ref_from(), val1)

