"""All the views used. An additional tx_hash field is added
when document is succesfully validated. It stores hash of
corresponding Ethereum transaction."""

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
import copy

from ubitquity.ubitquity.ssh_client import SSHClient
from .models import BillOfSale, ApplicationForRegistration, SecurityGuarantee, Document
from .serializers import BillOfSaleSerializer, ApplicationForRegistrationSerializer, SecurityGuaranteeSerializer, \
    DocumentCreateSerializer, DocumentSerializer
from .utils import Contract


class BillOfSaleListView(generics.ListCreateAPIView):
    """
    get:
    Return a full list of Bill of Sales stored. An additional _tx_hash_ field is returned and contains ID of relevant ETH transaction. 

    post:
    Create a new Bill of Sale and store it as smart contract in Ethereum network.
    """

    queryset = BillOfSale.objects.all()
    serializer_class = BillOfSaleSerializer

    def perform_create(self, serializer):
        bos_contract = Contract()
        bos_contract.content = copy.copy(serializer.validated_data)
        bos_contract.hash()
        hsh = bos_contract.deploy()
        serializer.save(tx_hash = hsh)


class DocumentOnchainView(APIView):
    def get(self, request, tx_hash):
        """
        Return details of the document directly from corresponding smart contract in blockchain. 
        """
        if tx_hash:
            contract = Contract()
            contract_stored = contract.read(tx_hash)
            if contract_stored:
                return Response(contract_stored)
            return Response({})


class ApplicationForRegistrationListView(generics.ListCreateAPIView):
    """
    get:
    Return a full list of Applications for Registration stored. An additional _tx_hash_ field is returned and contains ID of relevant ETH transaction. 

    post:
    Create a new Application for Registration and store it as smart contract in Ethereum network.
    """

    queryset = ApplicationForRegistration.objects.all()
    serializer_class = ApplicationForRegistrationSerializer

    def perform_create(self, serializer):
        afr_contract = Contract()
        afr_contract.content = copy.copy(serializer.validated_data)
        afr_contract.hash()
        hsh = afr_contract.deploy()
        serializer.save(tx_hash=hsh)


class SecurityGuaranteeListView(generics.ListCreateAPIView):
    """
    get:
    Return a full list of Security Guarantees stored. An additional _tx_hash_ field is returned and contains ID of relevant ETH transaction. 

    post:
    Create a new Security Guarantee and store it as smart contract in Ethereum network.
    """
    queryset = SecurityGuarantee.objects.all()
    serializer_class = SecurityGuaranteeSerializer

    def perform_create(self, serializer):
        g_contract = Contract()
        g_contract.content = copy.copy(serializer.validated_data)
        g_contract.hash()
        hsh = g_contract.deploy()
        serializer.save(tx_hash = hsh)


class DocumentCreateView(generics.CreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # push the serialized data to ubitquit servers
        client = SSHClient()
        data = DocumentSerializer(instance=serializer.instance).data
        client.put_data(data=data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class DocumentView(generics.RetrieveAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
