import fitz

def create_test_exam_pdf(filename: str):
    doc = fitz.open()
    page = doc.new_page()
    
    content = """
    Student ID: STU001
    Name: Test Student
    
    Question 1: Explain the OSI model and its layers.
    
    The OSI model stands for Open Systems Interconnection model.
    It has 7 layers: Physical, Data Link, Network, Transport,
    Session, Presentation, and Application layer.
    The Physical layer deals with raw bits transmitted over cables.
    The Data Link layer handles error detection and MAC addresses.
    The Network layer handles routing using IP addresses.
    The Transport layer ensures reliable delivery using TCP protocol.
    For example, when you browse a website, HTTP works at the
    Application layer while TCP works at the Transport layer.
    
    Question 2: What is TCP/IP and how does it differ from UDP?
    
    TCP stands for Transmission Control Protocol. It is a 
    connection oriented protocol that ensures reliable delivery
    of data packets between systems.
    UDP stands for User Datagram Protocol. It is connectionless
    and does not guarantee delivery of packets.
    Key differences: TCP is reliable but slower, UDP is faster
    but unreliable. TCP uses handshaking, UDP does not.
    """
    
    page.insert_text((50, 50), content, fontsize=11)
    doc.save(filename)
    doc.close()
    print(f"✅ Test PDF created: {filename}")

create_test_exam_pdf("samples/test_student_001.pdf")