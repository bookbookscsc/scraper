from setuptools import setup, find_packages

setup_requires = []

install_requires = [
    'requests-html==0.9.0'
]

dependency_links = []

setup(
    name='book_review_scraper',
    version='0.2',
    description='simple book review scraper',
    author='minomi',
    author_email='5minhominho@gmail.com',
    url='https://github.com/bookbookscsc/scraper',
    python_requires='>=3.6.0',
    license='MIT',
    install_requires=install_requires,
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    keywords=['book', 'review'],
    classifiers=[
        # 프로젝트가 어느 단계에 있는가? 일반적인 값은
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # 어느 독자를 대상으로 만들어진 프로젝트인지 표시하라
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # 지원하는 파이썬 버전을 지정하라. 특히, 파이썬2, 파이썬 3 또는 둘 다를
        # 지원하는지 반드시 표기하라.
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ]
)