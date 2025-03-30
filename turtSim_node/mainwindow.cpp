#include "mainwindow.h"
#include "./ui_mainwindow.h"
#include <QDebug>
#include <signal.h>
#include <unistd.h>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
    , rosProcess(new QProcess(this))
{
    ui->setupUi(this);
}

MainWindow::~MainWindow()
{
    // Ensure process termination when closing the app.
    if (rosProcess->state() == QProcess::Running) {
        // Send termination to the process group
        qint64 pid = rosProcess->processId();
        ::kill(-pid, SIGTERM);
        rosProcess->waitForFinished(3000);
    }
    delete ui;
}

void MainWindow::on_pushButton_clicked()
{
    if (rosProcess->state() == QProcess::Running)
    {
        qDebug() << "Turtlesim node is already running.";
        return;
    }

    // Use bash with setsid to launch the process in its own group.
    QString command = "bash";
    QStringList args;
    args << "-c" << "exec setsid ros2 run turtlesim turtlesim_node";

    rosProcess->start(command, args);

    if (!rosProcess->waitForStarted())
    {
        qCritical() << "Failed to start turtlesim_node: " << rosProcess->errorString();
    }
    else
    {
        qDebug() << "Turtlesim node started successfully!";
    }
}

void MainWindow::on_pushButton_2_clicked()
{
    if (rosProcess->state() == QProcess::Running)
    {
        qint64 pid = rosProcess->processId();
        // Send SIGTERM to the entire process group using negative PID.
        if (::kill(-pid, SIGTERM) == -1)
        {
            qWarning() << "Failed to send SIGTERM to turtlesim process group.";
        }
        if (!rosProcess->waitForFinished(5000))
        {
            qWarning() << "Turtlesim node did not terminate in time: forcing kill.";
            ::kill(-pid, SIGKILL);
        }
        else
        {
            qDebug() << "Turtlesim node stopped successfully.";
        }
    }
    else
    {
        qDebug() << "Turtlesim node is not running";
    }
}
