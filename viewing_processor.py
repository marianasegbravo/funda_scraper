from fundascraping.viewing_requester import ViewingRequester
import sys

# example python viewing_processor.py 70 Ommoord,Blijdorp 2
def main(m2, neighborhoods, bedrooms):

    # Create an instance of the class
    request_viewings = ViewingRequester(m2=m2, neighborhoods=neighborhoods, bedrooms=bedrooms)

    # Process viewings
    request_viewings.process_viewing_requests()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python viewing_processor.py m2 neighborhood1,neighborhood2 bedrooms")
        sys.exit(1)

    m2 = int(sys.argv[1])
    neighborhoods = sys.argv[2].split(',')
    bedrooms = int(sys.argv[3])

    main(m2, neighborhoods, bedrooms)