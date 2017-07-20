def hello(job):
    print("Hello", job)
    with job:
        with open('hello.txt', 'w') as f:
            f.write('world!')


if __name__ == '__main__':
    import flow
    flow.run()
