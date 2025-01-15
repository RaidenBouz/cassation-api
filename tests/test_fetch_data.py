import tarfile
from io import BytesIO
from unittest.mock import Mock

from lxml import etree as ET

from scripts.fetch_data import (clean_content, fetch_and_store_decisions,
                                fetch_tar_urls, process_tar_file,
                                save_decisions_to_db)
from src.models import Decision, db


def test_fetch_tar_urls(mock_requests):
    # Mock the HTML response with tar.gz links
    mock_response = Mock()
    mock_response.content = b"""
    <html>
        <body>
            <a href="file1.tar.gz">File 1</a>
            <a href="file2.tar.gz">File 2</a>
            <a href="file.txt">Not a tar file</a>
        </body>
    </html>
    """
    mock_requests.return_value = mock_response

    tar_urls = fetch_tar_urls("http://example.com")

    # Assert the correct URLs are returned
    assert len(tar_urls) == 2
    assert "http://example.com/file1.tar.gz" in tar_urls
    assert "http://example.com/file2.tar.gz" in tar_urls


def test_clean_content():
    # Create a sample XML element
    xml_content = """
    <CONTENU>
        <p>Hello <br/>World</p>
        <p>This is a test.</p>
    </CONTENU>
    """
    root = ET.fromstring(xml_content)

    cleaned_content = clean_content(root)

    y
    assert cleaned_content == "Hello \nWorld This is a test."


def test_process_tar_file(mock_requests, app):
    # Create a tar.gz buffer with a single XML file
    tar_buffer = BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w:gz") as tar:
        xml_content = """
        <root>
            <META_COMMUN><ID>1</ID></META_COMMUN>
            <META_JURI><TITRE>Test Decision</TITRE></META_JURI>
            <META_JURI_JUDI><FORMATION>Formation A</FORMATION></META_JURI_JUDI>
            <CONTENU><p>Test content</p></CONTENU>
        </root>
        """
        tar_info = tarfile.TarInfo("decision_1.xml")
        tar_info.size = len(xml_content)
        tar.addfile(tar_info, BytesIO(xml_content.encode()))
    tar_buffer.seek(0)

    # Mock the requests.get call to return the tar buffer
    mock_requests.return_value = Mock(raw=tar_buffer)

    decisions = process_tar_file("http://example.com/file.tar.gz", app)

    # Assert the decisions are processed correctly
    assert len(decisions) == 1
    assert decisions[0]["id"] == "1"
    assert decisions[0]["title"] == "Test Decision"
    assert decisions[0]["formation"] == "Formation A"
    assert decisions[0]["content"] == "Test content"


# tests/test_script.py
def test_save_decisions_to_db(app):
    with app.app_context():
        # Clear the database before the test
        db.session.query(Decision).delete()
        db.session.commit()

        # Create test decisions
        decisions = [
            {
                "id": "1",
                "title": "Test Decision 1",
                "formation": "Formation A",
                "content": "Content 1",
            },
            {
                "id": "2",
                "title": "Test Decision 2",
                "formation": "Formation B",
                "content": "Content 2",
            },
        ]

        # Call the function and pass the app object
        save_decisions_to_db(decisions, app)

        # Assert the decisions are saved to the database
        assert Decision.query.count() == 2

        # Verify the first decision
        decision_1 = Decision.query.filter_by(id="1").first()
        assert decision_1.title == "Test Decision 1"
        assert decision_1.formation == "Formation A"
        assert decision_1.content == "Content 1"

        # Verify the second decision
        decision_2 = Decision.query.filter_by(id="2").first()
        assert decision_2.title == "Test Decision 2"
        assert decision_2.formation == "Formation B"
        assert decision_2.content == "Content 2"


def test_save_decisions_to_db_duplicates(app):
    with app.app_context():
        # Clear the database before the test
        db.session.query(Decision).delete()
        db.session.commit()

        # Add a decision to the database
        decision = Decision(
            id="1", title="Test Decision", formation="Formation A", content="Content"
        )
        db.session.add(decision)
        db.session.commit()

        # Create test decisions with a duplicate ID
        decisions = [
            {
                "id": "1",
                "title": "Duplicate Decision",
                "formation": "Formation B",
                "content": "Duplicate Content",
            },
            {
                "id": "2",
                "title": "New Decision",
                "formation": "Formation C",
                "content": "New Content",
            },
        ]

        # Call the function and pass the app object
        save_decisions_to_db(decisions, app)

        # Assert only the new decision is saved
        assert Decision.query.count() == 2
        assert (
            Decision.query.filter_by(id="1").first().title == "Test Decision"
        )  # Original decision
        assert (
            Decision.query.filter_by(id="2").first().title == "New Decision"
        )  # New decision


# tests/test_script.py
def test_fetch_and_store_decisions(mock_requests, app):
    with app.app_context():
        # Clear the database before the test
        db.session.query(Decision).delete()
        db.session.commit()

        # Mock the base URL response
        mock_base_response = Mock()
        mock_base_response.content = b"""
        <html>
            <body>
                <a href="file1.tar.gz">File 1</a>
            </body>
        </html>
        """
        mock_requests.return_value = mock_base_response

        # Create a tar.gz buffer with a single XML file
        tar_buffer = BytesIO()
        with tarfile.open(fileobj=tar_buffer, mode="w:gz") as tar:
            xml_content = """
            <root>
                <META_COMMUN><ID>1</ID></META_COMMUN>
                <META_JURI><TITRE>Test Decision</TITRE></META_JURI>
                <META_JURI_JUDI><FORMATION>Formation A</FORMATION></META_JURI_JUDI>
                <CONTENU><p>Test content</p></CONTENU>
            </root>
            """
            tar_info = tarfile.TarInfo("decision_1.xml")
            tar_info.size = len(xml_content)
            tar.addfile(tar_info, BytesIO(xml_content.encode()))
        tar_buffer.seek(0)

        # Mock the requests.get call for the tar file
        mock_requests.side_effect = [mock_base_response, Mock(raw=tar_buffer)]

        fetch_and_store_decisions("http://example.com", app)

        # Assert the decision is saved to the database
        assert Decision.query.count() == 1
        decision = Decision.query.filter_by(id="1").first()
        assert decision.title == "Test Decision"
        assert decision.formation == "Formation A"
        assert decision.content == "Test content"
