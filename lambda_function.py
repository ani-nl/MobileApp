import json
import psycopg2

# File number F0001
# Real file name: loginMember.py
# Code to register and login

# ErrorCodes
# 1001 - DB connection creation failed.
db_conn_failed = 1001
db_operation_failed = 1002
# 1003 - 

db_host = "appdb.cjj7zdnu6qi7.eu-west-2.rds.amazonaws.com"
db_port = 5432
db_name = "postgres"
db_user = "postgres"
db_pass = "EfvYxcOvGXF18YSxJFiJ"
conn = None

class Member:
  # login = 1, when user is valid
  # login = 0, when user is blocked - not yet implemented in DB
  def __init__(self, email, fname, ID=0, loginStatus=1):
    self.email = email
    self.fname = fname
    self.ID = ID
    self.loginStatus = loginStatus
    self.hhID = -1
    printTrace("At line Member.init # 30")
    
  def setID(self, ID, loginStatus=1):
    self.ID = ID
    self.loginStatus = loginStatus
    printTrace("At line Member.setID # 35")

  def getID(self):
    printTrace("At line Member.getID # 38")
    return self.ID

  def getEmail(self):
    printTrace("At line Member.getEmail # 42")
    return self.email

  def getFname(self):
    printTrace("At line Member.getFname # 46")
    return self.fname

  def createJSON(self):
    # retVal is a string
    retVal = json.dumps(self.__dict__)
    printTrace("At line Member.createJSON # 52")
    return retVal
    
  def validateMember(self, conn):
    # returns 0 if member is not found
    # returns -1 if more than 1 members found (system error)
    #  taken care at DB level. This should never be the case
    # return 1 if the member is found
    printTrace("At line Member.vlidateMember # 60")

    query = "select id, tbl_members_fname from tbl_members where tbl_members_email='"+self.email+"'"
    cursor = conn.cursor()
    cursor.execute(query)
    if (0 == cursor.rowcount):
      return 0
    elif (1 == cursor.rowcount):
      member = cursor.fetchone()
      self.ID = member[0]
      self.fname = member[1]
      return 1
    
    # This should never happen, else something is wrong in the DB
    return -1

  def addMember(self, conn):
    # returns 0 for success, 1 for failure
    printTrace("At line Member.addMember # 78")
    query = "insert into tbl_members (tbl_members_email, tbl_members_fname) values ('{email}','{fname}') returning id".format(
      email=self.email,fname=self.fname)

    try:
      cursor = conn.cursor()
      cursor.execute(query)
      self.ID = cursor.fetchone()[0]
      conn.commit()
      return 0
    except Exception as error:
      print("DB operation failed.\n{0}".format(error))
      return 1
# class Member ends here

def printTrace(msg):
  i = 0
  # print(msg)

def create_conn():
  global conn
  printTrace("At line create_conn # 98")
  try:
    conn = psycopg2.connect("dbname={} user={} host={} password={}".format(db_name,db_user,db_host,db_pass))
  except Exception as error:
    print("Cannot connect.\n{0}".format(error))
  return conn


def generateErrorResponse(errorCode, details):
  printTrace("At line generateErrorResponse # 107")
  return {
        'statusCode': 200,
        'body': json.dumps({ 'code':errorCode,
                             'details':details })
    }  


def generateSuccessResponse(email, ID, fname):
  printTrace("At line generateSuccessResponse # 116")
  return {
        'statusCode': 200,
        'body': json.dumps({ 'code':0,
                             'body': { 'email':email,
                                       'ID': ID,
                                       'fname': fname } })
    }  


def lambda_handler(event, context):
  # Request structure - {"member":"a.b@c.co"}
  # get the DB connection
  
  global conn
  if (None == conn):
    conn = create_conn()
    if (None == conn):
      return generateErrorResponse(db_conn_failed, context.aws_request_id)

  printTrace("At line lambda_handler # 136")
  # get the user request as a string
  reqStr = event['body']
  
  print("reqStr ",reqStr)
  
  # reqJson is a dict
  reqJson = json.loads(reqStr)
  memberEmail = reqJson["member"]
  fname = reqJson["fname"]
  
  printTrace("At line lambda_handler # 134")

  # create member object
  member = Member(memberEmail, fname)
  a = conn.cursor()
  retVal = member.validateMember(conn)
  if (1 == retVal):
    # success msg; loginStatus not yet handled
    return generateSuccessResponse(member.getEmail(), member.getID(), member.getFname())
  elif (0 == retVal):
    # create new member
    if (1 == member.addMember(conn)):
      return generateErrorResponse(db_operation_failed, context.aws_request_id)
    else:
      # success msg; loginStatus not handled
      return generateSuccessResponse(member.getEmail(), member.getID(), member.getFname())
  else:
    print("Code should never reach here - loc#0124")
    return {
        'statusCode': 500,
        'body': json.dumps('Failure report - LOC_F0001_L00140')
    }
# member1 = Member("ani@dan.com",1)
# print(member1.__dict__)
# print(member1.createJSON())
# event = {"body":{"member":"a.b@c.co","fname":"Ani"}}
# context = {"aws_request_id":"Req1"}
# lambda_handler(event, context)
