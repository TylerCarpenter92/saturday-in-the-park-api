"""View module for handling requests about park areas"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from kennywoodapi.models import Itinerary, ParkArea, Attraction, Customer


class ItineraryItemSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for park areas

    Arguments:
        serializers
    """

    class Meta:
        model = Itinerary
        url = serializers.HyperlinkedIdentityField(
            view_name='itineraryitem',
            lookup_field='id'
        )
        fields = ('id', 'url', 'attraction', 'starttime')
        depth = 1


class ItineraryItems(ViewSet):
    """Park Areas for Kennywood Amusement Park"""

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized Attraction instance
        """
        new_itinerary_item = Itinerary()
        new_itinerary_item.customer = Customer.objects.get(user=request.auth.user)
        new_itinerary_item.starttime = request.data["starttime"]

        attraction = Attraction.objects.get(pk=request.data["ride_id"])
        new_itinerary_item.attraction = attraction
        new_itinerary_item.save()

        serializer = ItineraryItemSerializer(new_itinerary_item, context={'request': request})

        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single park area

        Returns:
            Response -- JSON serialized park area instance
        """
        try:
            itinerary_item = Itinerary.objects.get(pk=pk)
            serializer = ItineraryItemSerializer(itinerary_item, context={'request': request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """Handle PUT requests for a park area attraction

        Returns:
            Response -- Empty body with 204 status code
        """
        itinerary_item = Itinerary.objects.get(pk=pk)
        itinerary_item.starttime = request.data["starttime"]
        itinerary_item.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single park are

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            itinerary_item = Itinerary.objects.get(pk=pk)
            itinerary_item.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Attraction.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests to park attractions resource

        Returns:
            Response -- JSON serialized list of park attractions
        """
        customer =  Customer.objects.get(user=request.auth.user)

        itineraryItems = Itinerary.objects.filter(customer=customer)

        # Support filtering attractions by area id


        serializer = ItineraryItemSerializer(
            itineraryItems, many=True, context={'request': request})
        return Response(serializer.data)
