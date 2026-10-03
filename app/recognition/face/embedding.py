import insightface


class FaceEmbedding:

    def __init__(self):

        print("Loading face recognition model...")

        self.model = insightface.app.FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"]
        )

        self.model.prepare(
            ctx_id=0,
            det_size=(640, 640)
        )

        print("Face recognition model loaded.")

    def get_faces(self, frame):
        """
        Detect faces and generate face embeddings.
        """

        return self.model.get(frame)

    def get_embedding(self, frame):
        """
        Return the embedding of the first detected face.
        """

        faces = self.get_faces(frame)

        if not faces:
            return None

        return faces[0].embedding