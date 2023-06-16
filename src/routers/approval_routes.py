from fastapi import APIRouter

from controllers.approvals import (
    CreateApprovalFlowController,
    CreateApprovalRequestController,
    ProcessApprovalRequestController,
    ApprovalRequestDetailsController,
    GetSmApproverListController,
    GetApprovalFlowListForSMController,
    UpdateApprovalFlowController,
)
from controllers.approvals.approvals_access import ApprovalsAccessController


class ApprovalFlowRoutesGroup:
    prefix = "/approvals/approvalflow"

    def __init__(
        self,
        create_approval_flow_controller_route: CreateApprovalFlowController,
        get_sm_approval_flow_list_controller_route: GetApprovalFlowListForSMController,
        update_approval_flow_controller_route: UpdateApprovalFlowController,
    ) -> None:

        router = APIRouter(tags=["ApprovalFlow"])

        router.post(
            path="/create",
        )(create_approval_flow_controller_route.createApprovalFlowController)

        router.get(
            path="/smapprovalflowlist/{smid}",
        )(get_sm_approval_flow_list_controller_route.getApprovalFlowListForSM)

        router.patch(
            path="/{approvalflowid}",
        )(update_approval_flow_controller_route.update_approval_flow)

        self.router = router


class ApprovalRequestRoutesGroup:
    prefix = "/approvals/approvalrequest"

    def __init__(
        self,
        create_approval_request_controller_route: CreateApprovalRequestController,
        process_approval_request_controller_route: ProcessApprovalRequestController,
        approval_request_details_controller_route: ApprovalRequestDetailsController,
    ) -> None:

        router = APIRouter(tags=["ApprovalRequest"])

        router.get(
            path="/details",
        )(approval_request_details_controller_route.approvalRequestDetailController)

        router.post(
            path="/create",
        )(create_approval_request_controller_route.createApprovalRequestController)

        router.post(
            path="/process",
        )(process_approval_request_controller_route.processApprovalRequestController)

        self.router = router


class ApproverRoutesGroup:
    prefix = "/approvals"

    def __init__(
        self,
        get_sm_approver_list_controller_route: GetSmApproverListController,
        approvals_access_controller: ApprovalsAccessController
    ) -> None:

        router = APIRouter(tags=["Approver"])

        router.post(
            path="/smcollaboratorlist",
        )(get_sm_approver_list_controller_route.get_sm_collaborator_list)
        router.get(
            path="/check-access",
        )(approvals_access_controller.has_access)

        self.router = router

class InternalRoutesGroup:
    prefix = "/internal"

    def __init__(
        self,
        approval_request_details_controller: ApprovalRequestDetailsController,
    ) -> None:

        router = APIRouter(tags=["Internal"])

        router.get(
            path="/approvers",
        )(approval_request_details_controller.fetch_approvers)

        self.router = router