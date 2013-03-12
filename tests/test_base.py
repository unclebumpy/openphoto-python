import unittest
import openphoto

try:
    import tokens
except ImportError:
    print ("********************************************************************\n"
           "You need to create a 'tokens.py' file containing the following:\n\n"
           "   host = \"<test_url>\"\n"
           "   consumer_key = \"<test_consumer_key>\"\n"
           "   consumer_secret = \"<test_consumer_secret>\"\n"
           "   token = \"<test_token>\"\n"
           "   token_secret = \"<test_token_secret>\"\n"
           "   host = \"<hostname>\"\n\n"
           "WARNING: Don't use a production OpenPhoto instance for this!\n"
           "********************************************************************\n")
    raise

class TestBase(unittest.TestCase):
    TEST_TITLE = "Test Image - delete me!"
    TEST_TAG = "test_tag"
    TEST_ALBUM = "test_album"
    MAXIMUM_TEST_PHOTOS = 4 # Never have more the 4 photos on the test server

    def __init__(self, *args, **kwds):
        unittest.TestCase.__init__(self, *args, **kwds)
        self.photos = []

    @classmethod
    def setUpClass(cls):
        """ Ensure there is nothing on the server before running any tests """
        cls.client = openphoto.OpenPhoto(tokens.host,
                             tokens.consumer_key, tokens.consumer_secret,
                             tokens.token, tokens.token_secret)

        if cls.client.photos.list() != []:
            raise ValueError("The test server (%s) contains photos. "
                             "Please delete them before running the tests"
                             % tokens.host)

        if cls.client.tags.list() != []:
            raise ValueError("The test server (%s) contains tags. "
                             "Please delete them before running the tests"
                             % tokens.host)

        if cls.client.albums.list() != []:
            raise ValueError("The test server (%s) contains albums. "
                             "Please delete them before running the tests"
                             % tokens.host)

    @classmethod
    def tearDownClass(cls):
        """ Once all tests have finished, delete all photos, tags and albums"""
        cls._delete_all()

    def setUp(self):
        """
        Ensure the three test photos are present before each test.
        Give them each a tag.
        Put them into an album.
        """
        self.photos = self.client.photos.list()
        if len(self.photos) != 3:
            print "[Regenerating Photos]"
            if len(self.photos) > 0:
                self._delete_all()
            self._create_test_photos()
            self.photos = self.client.photos.list()

        self.tags = self.client.tags.list()
        if (len(self.tags) != 1 or
                self.tags[0].id != self.TEST_TAG or
                self.tags[0].count != "3"):
            print "[Regenerating Tags]"
            self._delete_all()
            self._create_test_photos()
            self.photos = self.client.photos.list()
            self.tags = self.client.tags.list()
        if len(self.tags) != 1:
            print "Tags: %s" % self.tags
            raise Exception("Tag creation failed")

        self.albums = self.client.albums.list()
        if (len(self.albums) != 1 or
                self.albums[0].name != self.TEST_ALBUM or
                self.albums[0].count != "3"):
            print "[Regenerating Albums]"
            self._delete_all()
            self._create_test_photos()
            self.photos = self.client.photos.list()
            self.tags = self.client.tags.list()
            self.albums = self.client.albums.list()
        if len(self.albums) != 1:
            print "Albums: %s" % self.albums
            raise Exception("Album creation failed")

    @classmethod
    def _create_test_photos(cls):
        """ Upload three test photos """
        album = cls.client.album.create(cls.TEST_ALBUM, visible=True)
        photos = [
            cls.client.photo.upload_encoded("tests/test_photo1.jpg",
                                            title=cls.TEST_TITLE,
                                            tags=cls.TEST_TAG),
            cls.client.photo.upload_encoded("tests/test_photo2.jpg",
                                            title=cls.TEST_TITLE,
                                            tags=cls.TEST_TAG),
            cls.client.photo.upload_encoded("tests/test_photo3.jpg",
                                            title=cls.TEST_TITLE,
                                            tags=cls.TEST_TAG),
            ]
        # Remove the auto-generated month/year tags
        tags_to_remove = [p for p in photos[0].tags if p != cls.TEST_TAG]
        for photo in photos:
            photo.update(tagsRemove=tags_to_remove, albums=album.id)

    @classmethod
    def _delete_all(cls):
        photos = cls.client.photos.list()
        if len(photos) > cls.MAXIMUM_TEST_PHOTOS:
            raise ValueError("There too many photos on the test server - must always be less than %d."
                             % cls.MAXIMUM_TEST_PHOTOS)
        for photo in photos:
            photo.delete()
        for tag in cls.client.tags.list():
            tag.delete()
        for album in cls.client.albums.list():
            album.delete()