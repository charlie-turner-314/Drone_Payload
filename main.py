import enviro.enviro_lcd as enviro
import web.backend.server as server

if __name__ == "__main__":
    # run both main functions in different threads
    server.main()
    enviro.main()
