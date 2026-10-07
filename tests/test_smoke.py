from src.app.main import main


def test_application_can_start(capsys):
    main()

    captured = capsys.readouterr()

    assert captured.out.strip() == "Anas Shop Customer Support Copilot MLP"