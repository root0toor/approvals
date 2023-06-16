import string
import random

def generate_approval_flow_name():
    str_len = 7
    generated_str = 'Test Approval ' + str(''.join(random.choices(string.ascii_letters, k=str_len)))
    return generated_str

def generate_conversation_id():
    conversation_id = random.randint(1, 1000)
    return conversation_id
    
class TestData:
    HOST = "https://localhost:8000"
    
    admin_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOjEsInVzZXJncm91cGlkIjoxLCJzbWlkcyI6WzFdLCJpc19hZG1pbiI6dHJ1ZSwicGVybWlzc2lvbnMiOltdLCJleHAiOjE3NjU2NDAwNjYuMzYzMzEzN30.5EpDrqUgmSUPLnv_aSHUc3xmLTltHHDk28hcG4Ws-Y4"
    
    sm_member_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOjIsInVzZXJncm91cGlkIjoxLCJzbWlkcyI6WzFdLCJpc19hZG1pbiI6ZmFsc2UsInBlcm1pc3Npb25zIjpbInNtLnBhcnRpYWwiLCJmdWxsIl0sImV4cCI6MTc2NTY0MDMxMi44MDQwMDM1fQ._lr6MVcPZVn8V003AGtIlKEUI299cA-R7mZKwfzVG10"

    initial_step_collab_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjb2xsYWJvcmF0b3JfaWQiOjgsImV4cCI6MTc2NTYzOTIxNi4wNDg3OTI2fQ.T9td4WaKdXRflm3ezXIFV83j24tHzbid2ljUBA3Rwho"

    initial_step_hiver_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaWQiOjEsInVzZXJncm91cGlkIjoxLCJzbWlkcyI6WzFdLCJpc19hZG1pbiI6dHJ1ZSwicGVybWlzc2lvbnMiOltdLCJleHAiOjE3NjU2NDExODYuNTk0OTM0NX0.xpOMBL6nMj9hsCrlwyXmDQlFuChuA3SYvYcoWU_B0J8"

    next_step_collab_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjb2xsYWJvcmF0b3JfaWQiOjEwLCJleHAiOjE3NjU2MzkzMjguOTkwMTA1Nn0.hYZD_8yfj4-zvRLBcau8F54or21FFMS--B2WfZNGMBI"

    create_approval_flow_payload = {
        "name": generate_approval_flow_name(),
        "smId": 1,
        "steps": [
            [{"type":"COLLABORATOR", "value":"shivam@gmail.com"},{"type":"HIVER", "value":1}],[{"type":"COLLABORATOR", "value":9}]
        ]
    }
    
    create_approval_request_payload = {
        "approval_flow_id": None,
        "conversation_id": generate_conversation_id()
    }
    
    process_approval_request_payload = {
        "approval_request_id": None,
        "status": "APPROVED",
        "reason":"",
        "note":""
    }

    