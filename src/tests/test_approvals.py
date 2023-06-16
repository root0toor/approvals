from .test_data import TestData

class TestApprovals:
    
    """for testing purpose, limit the no. of steps upto 2 while creating approval flow"""
    
    conversation_id = None
    
    def test_create_approval_flow(self,client):
        HOST = TestData.HOST
        BASE_URL = "/approvals/approvalflow/create"
        response = client.post(HOST + BASE_URL ,json=TestData.create_approval_flow_payload,headers={"Authorization": "Bearer " + TestData.admin_token})
        print("*****************",response.text)
        TestData.create_approval_request_payload["approval_flow_id"] = response.json()["data"]["approval_flow"]["id"]
        assert response.status_code == 201
        assert response.json()["message"] == ["Approval flow created successfully"]
        
    def test_create_approval_request(self,client):
        HOST = TestData.HOST
        BASE_URL = "/approvals/approvalrequest/create"
        response = client.post(HOST + BASE_URL ,json=TestData.create_approval_request_payload,headers={"Authorization": "Bearer " + TestData.sm_member_token})
        print("*****************",response.text)
        TestApprovals.conversation_id = TestData.create_approval_request_payload["conversation_id"]
        
        assert response.status_code == 201
        assert response.json()["message"] == ["Approval request created successfully"]
    
    def test_get_approval_request_details(self,client):
        HOST = TestData.HOST
        BASE_URL = f"/approvals/approvalrequest/details/{TestApprovals.conversation_id}"
        response = client.get(HOST + BASE_URL ,headers={"Authorization": "Bearer " + TestData.sm_member_token})
        print("*****************",response.text)
        TestData.process_approval_request_payload["approval_request_id"] = response.json()["data"]["approval_request_info"]["id"]
        assert response.status_code == 200
        assert response.json()["message"] == ["Approval request details"]

    def test_process_approval_request(self,client):
        no_of_steps = len(TestData.create_approval_flow_payload["steps"])
        for step in range(no_of_steps):
            if step == 0:
                approver_token = TestData.initial_step_hiver_token 
            else:
                approver_token = TestData.next_step_collab_token
            HOST = TestData.HOST
            BASE_URL = "/approvals/approvalrequest/process"
            response = client.post(HOST + BASE_URL ,json=TestData.process_approval_request_payload,headers={"Authorization": "Bearer " + approver_token})
            print("*****************",response.text)
            assert response.status_code == 200
            assert response.json()["message"] == ["Approval request processed successfully"]
    