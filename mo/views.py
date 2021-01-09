from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate, login

from .models import video,user,User
from .forms import VideoForm
import threading
import cv2
import nltk
import operator
import mysql.connector
import socket
socket.getaddrinfo('localhost', 9999)
from nltk.stem.porter import PorterStemmer

porter_stemmer = PorterStemmer()
query_tokens_stemming_without_stopwords=[]

# Make Inverted index table
def insert(video_id,stemm,freq,pos):
    mydb = mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="textso"
    )
    mycursor = mydb.cursor()
    sql = "INSERT INTO inverted_index (Video_ID,stemm,frequancy_counter,position) VALUES (%s,%s,%s,%s)"
    val = (video_id,stemm,freq,pos)
    mycursor.execute(sql, val)
    mydb.commit()
#------------------------------------------------------------------------------------
def Inverted_Index(stemming_list,tokens , videoId):
    #get frequency for each word in each description
    frequancy_counter = 0;
    prevent_repeat=[]
    for stemm in stemming_list:
        if (prevent_repeat.__contains__(stemm)==False):
            for another_stemm in stemming_list:
                if (another_stemm == stemm):
                    frequancy_counter = frequancy_counter + 1
            #add to database invered_index table
            insert(videoId,stemm,frequancy_counter,get_positions(stemm,tokens))
            prevent_repeat.append(stemm)
            frequancy_counter = 0
#------------------------------------------------------------------------------------
def get_positions(term,tokens):
    pos = ""
    i = 1
    for tok in tokens:
        if (porter_stemmer.stem(tok) == term):
            if (pos == ""):
                pos = pos + str(i)
            else:
                pos = pos + "," + str(i)
        i = i + 1
    return pos
#------------------------------------------------------------------------------------
def Parsing(desc, videoId):
    # make tokenization and split description with stopwords to use it in positions.
    tokens = nltk.word_tokenize(desc.lower())
    # ------------------------------------------------------------------------------------
    # remove Stop Words and convert word to his stemmer.
    stemming_tokens_without_stopwords = []
    for word in tokens:
        if (stop_words.__contains__(word) == False):
            stemming_tokens_without_stopwords.append(porter_stemmer.stem(word))
    # ------------------------------------------------------------------------------------
    Inverted_Index(stemming_tokens_without_stopwords,tokens ,videoId )
####################################################################################################
class word_details():
    def __init__(self, word_number, document_ID, frequency, positions):
        self.word_number = word_number
        self.document_ID = document_ID
        self.frequency = frequency
        self.positions = positions
#-----------------------------------------------------------------------------------------------------------------------
class retrieval_video_details():
    def __init__(self, score, docID, freq):
        self.score = score
        self.docID = docID
        self.freq = freq
#-----------------------------------------------------------------------------------------------------------------------
class only_1word_struct():
    def __init__(self, ID, Frequancy):
        self.ID = ID
        self.Frequancy = Frequancy
#-----------------------------------------------------------------------------------------------------------------------
only_1word_query_list=[]
all_related_videos = []
retrieval_videos = []
#-----------------------------------------------------------------------------------------------------------------------
def select_related_videos_descriptions():
    if (len(query_tokens_stemming_without_stopwords) == 1):
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="textso"
        )
        mycursor = mydb.cursor()
        sql = """SELECT Video_ID,frequancy_counter FROM inverted_index WHERE stemm=%s"""
        mycursor.execute(sql, (query_tokens_stemming_without_stopwords[0],))
        myresult = mycursor.fetchall()
        for aa in myresult:
            only_1word_query_list.append(only_1word_struct(aa[0], aa[1]))
        only_1word_query_list.sort(key=operator.attrgetter('Frequancy'),reverse=True)
    else:
        word_index = 1
        for stem in query_tokens_stemming_without_stopwords:
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="textso"
            )
            mycursor = mydb.cursor()
            sql = """SELECT Video_ID,frequancy_counter,position FROM inverted_index WHERE stemm=%s"""
            mycursor.execute(sql, (stem,))
            myresult = mycursor.fetchall()
            for aa in myresult:
                all_related_videos.append(word_details(word_index, aa[0], aa[1], aa[2]))
            word_index = word_index + 1
#-----------------------------------------------------------------------------------------------------------------------
def find_common_videos_descriptions():
    query_words_positions = []
    for pp in range(1,len(query_tokens_stemming_without_stopwords) + 1):
        query_words_positions.append(pp)
    for i in all_related_videos:
        score_sum = 0
        for word_pos in query_words_positions:
            if (i.word_number == word_pos):
                score1 = 100000
                for j in all_related_videos:
                    if ((j.word_number == word_pos + 1) & (i.document_ID == j.document_ID)):
                        pos1 = i.positions.split(',')
                        pos2 = j.positions.split(',')
                        for t1 in pos1:
                            for t2 in pos2:
                                sc = int(t2) - int(t1)
                                if ((sc > 0) & (sc < score1)):
                                    score1 = sc
                if (score1 != 100000):
                    score_sum = score_sum + score1
        if(score_sum != 0):
            if (retrieval_videos.__contains__(retrieval_video_details(score_sum, i.document_ID,i.frequency)) == False):
                retrieval_videos.append(retrieval_video_details(score_sum, i.document_ID,i.frequency))
    retrieval_videos.sort(key = operator.attrgetter('score'))
#-----------------------------------------------------------------------------------------------------------------------
####################################################################################################
semaphore = threading.Semaphore(1)

def LoadVideosFromDb():
    ListOfVideosName = []
    ConC = "D:/"
    list = video.objects.all()
    for i in range(0, len(list)):
        ListOfVideosName.append(ConC+str(list[i].videofile))
    for i in ListOfVideosName:
        print(i)
    return ListOfVideosName
####################################################################################################
def GetImageDescriptor(frame):
    frame = cv2.resize(frame, None, fx=0.5, fy=0.5)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    sift = cv2.xfeatures2d.SIFT_create() # Initiate sift detector
    kp, desc = sift.detectAndCompute(gray, None) # find the keypoints and descriptor with sift
    return desc
####################################################################################################
def GetVideoDescriptors(VideoName):
    print(VideoName)
    print("__________________________________________________")
    DescriptorList=[]
    capture = cv2.VideoCapture(VideoName)
    frameRate = int(capture.get(cv2.CAP_PROP_FPS)) - 1 #Num Of Frame Per Second (frameRate)
    FramePtr = 0    #in first Frame
    while capture.isOpened():
        capture.set(cv2.CAP_PROP_POS_FRAMES, FramePtr) #Set capture in Frame Position >> FramePtr
        flag, Frame = capture.read()
        if flag == False:
            break
        Descriptor=GetImageDescriptor(Frame)
        DescriptorList.append(Descriptor)
        FramePtr=FramePtr+frameRate
    semaphore.acquire()
    VideosNames1.append(VideoName)
    VideosFeatures.append(DescriptorList)
    print(VideoName)
    print("**************************************************")
    semaphore.release()
####################################################################################################
def FeatureMatching(imageFeature,FeatureOfVideo,VideoName):
    # create BFMatcher object
    bf = cv2.BFMatcher()
    NumOfGoodPoint=[]
    GoodPoint = []
    ratio = 0.6     # match for 60/100
    for feature in FeatureOfVideo:
        # Match descriptors.
        matches = bf.knnMatch(imageFeature, feature, k=2)
        for C1, C2 in matches:
            if C1.distance < ratio * C2.distance:
                GoodPoint.append(C1)
        NumOfGoodPoint.append(len(GoodPoint))
        GoodPoint.clear()
    semaphore.acquire()
    VideosNames2.append(VideoName)
    GoodPointsOfVideo.append(max(NumOfGoodPoint))
    semaphore.release()
####################################################################################################
def ExtractFeaturesFromVideos(ListOfVideosName):
    for video in ListOfVideosName:
        t = threading.Thread(target=GetVideoDescriptors, args=(video,))
        t.daemon = True
        t.start()
        threads.append(t)
    for x in threads:  # Wait for all of threads to finish
        x.join()
    threads.clear()
####################################################################################################
def Search(imageFeature):
    for i in range(0, len(VideosNames1)):
        t = threading.Thread(target=FeatureMatching, args=(imageFeature, VideosFeatures[i], VideosNames1[i],))
        t.daemon = True
        t.start()
        threads.append(t)
    for x in threads:  # Wait for all of threads to finish
        x.join()
    threads.clear()
####################################################################################################
def RankingTheVideos():
    GoodPointsOfVideo[::-1], VideosNames2[::-1] = zip(*sorted(zip(GoodPointsOfVideo, VideosNames2)))
####################################################################################################

def start_the_program(request):
    global VideosFeatures, VideosNames1, threads, GoodPointsOfVideo, VideosNames2
    VideosNames1 = []
    VideosFeatures = []
    threads = []
    GoodPointsOfVideo = []
    VideosNames2 = []
    ####################
    VideosNames1.clear()
    VideosFeatures.clear()
    VideosNames2.clear()
    GoodPointsOfVideo.clear()
    ListOfVideosName = LoadVideosFromDb() #When Start The Program
    ExtractFeaturesFromVideos(ListOfVideosName)
    #--------------------------------------------------------------------------------------------------------------
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="textso"
    )
    mycursor = mydb.cursor()
    mycursor.execute("TRUNCATE TABLE inverted_index")
    list = video.objects.all()
    for i in range(0, len(list)):
        Parsing(list[i].description,list[i].id)

    return HttpResponseRedirect('/')

def start(request):
    return render(request, '(0)Begin.html')

def landingpage(request):
    return render(request,'(1)start.html')

def signIn(request):
    u = request.POST['username2']
    p = request.POST['password2']
    request.session['username'] = u
    r = authenticate(username=u, password=p)
    if r is not None:
        login(request, r)
        return render(request, '(2)text.html',{'obj':u})
    else:
        s = '''
            <html>
                <head>
                <meta charset="UTF-8">
                <title>Welcome Page</title>
                <style> body{ color: red; }</style>
                </head>
                <body>
                    <h1 align='center'>User is not exist !! <br> Please Sign Up first !</h1>
                </body>
            </html>
            '''
        return HttpResponse(s)

def signUp(request):
    object = user()
    object.username = request.POST['un']
    object.password = request.POST['p']
    object.email = request.POST['e']
    djangoUser = User.objects.create_user(request.POST['un'], request.POST['e'], request.POST['p'])
    djangoUser.save()
    object.gender = request.POST['gridRadios']
    object.birthdate = request.POST['bd']
    object.save()
    return render(request,'(1)start.html')

def textSearch(request):
    return render(request, '(2)text.html')

def searchByText(request):
    query = request.POST.get('q',None).lower()
    query_tokens = query.split(' ')
    porter_stemmer = PorterStemmer()
    for i in query_tokens:
        if stop_words.__contains__(i) == False:
            query_tokens_stemming_without_stopwords.append(porter_stemmer.stem(i))
    select_related_videos_descriptions()
    if len(query_tokens_stemming_without_stopwords) == 1:
        rv = []
        for vid in only_1word_query_list:
            q1 = video.objects.get(id=vid.docID)
            rv.append("/media/"+str(q1.videofile))
    else:
        find_common_videos_descriptions()
        rv=[]
        for vid in retrieval_videos:
            q2 = video.objects.get(id=vid.docID)
            rv.append("/media/"+str(q2.videofile))
    context = {'rv': rv[3:]}
    rv.clear()
    return render(request, '(4)results.html',context)

def imageSearch(request):
    return render(request, '(3)image.html')

def searchByImage(request):
    loc = "D:\images\\"
    loc += request.FILES['image_file'].name
    print(str(loc))
    GoodPointsOfVideo.clear()
    VideosNames2.clear()
    img = cv2.imread(loc)
    ExtractFeaturesFromImage = GetImageDescriptor(img)
    Search(ExtractFeaturesFromImage)
    RankingTheVideos()
    retieved_video = []
    for i in range(0, len(VideosNames2)):
        print(VideosNames2[i])
        print(GoodPointsOfVideo[i])
        retieved_video.append("/media/"+VideosNames2[i][3:])
    context = {'rv': retieved_video}
    return render(request, '(4)results.html', context)

####################################################################################################
def f1(request):
    c = {'fn': 'mohsen', 'ln': 'ahmed', 'age': 20, 'l': [22, 23, 24]}
    return render(request, 'test.html',c)

def f2(request):
    s='''
    <html>
        <head>
        <meta charset="UTF-8">
        <title>Welcome Page</title>
        <style> body{ color: red; }</style>
        </head>
        <body>
            <h1 align='center'>WELCOME Django</h1>
        </body>
    </html>
    '''
    return HttpResponse(s)

def f3(request,n1,n2):
    s=n1+n2
    return HttpResponse("SUM = "+str(s))

def f4(request,a,b):
    return HttpResponse(a+str(b))

def f5(request,a,b,c):
    return HttpResponse(a+str(b+c))

def f6(request):
    lastvideo = video.objects.last()
    videofile = lastvideo
    form = VideoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
    context = {
                'videofile': videofile,
                'form': form
               }
    return render(request, 'videos.html', context)
####################################################################################################
stop_words = [
                "the",
                ".",
                ",",
                "a",
                "able",
                "about",
                "above",
                "according",
                "accordingly",
                "across",
                "actually",
                "after",
                "afterwards",
                "again",
                "against",
                "ain't",
                "all",
                "allow",
                "allows",
                "almost",
                "alone",
                "along",
                "already",
                "also",
                "although",
                "always",
                "am",
                "among",
                "amongst",
                "an",
                "and",
                "another",
                "any",
                "anybody",
                "anyhow",
                "anyone",
                "anything",
                "anyway",
                "anyways",
                "anywhere",
                "apart",
                "appear",
                "appreciate",
                "appropriate",
                "are",
                "aren't",
                "around",
                "as",
                "a's",
                "aside",
                "ask",
                "asking",
                "associated",
                "at",
                "available",
                "away",
                "awfully",
                "be",
                "became",
                "because",
                "become",
                "becomes",
                "becoming",
                "been",
                "before",
                "beforehand",
                "behind",
                "being",
                "believe",
                "below",
                "beside",
                "besides",
                "best",
                "better",
                "between",
                "beyond",
                "both",
                "brief",
                "but",
                "by",
                "came",
                "can",
                "cannot",
                "cant",
                "can't",
                "cause",
                "causes",
                "certain",
                "certainly",
                "changes",
                "clearly",
                "c'mon", "co", "com", "come", "comes",
                "concerning",
                "consequently",
                "consider",  "considering",
                "contain",
                "containing",  "contains",
                "corresponding",
                "could",
                "couldn't", "course",
                "c's",
                "currently", "definitely",
                "described",
                "despite",
                "did",
                "didn't",
                "different",
                "do",
                "does",
                "doesn't",
                "doing",
                "done",
                "don't",
                "down",
                "downwards",
                "during",
                "each",
                "edu",
                "eg",
                "eight",
                "either",
                "else",
                "elsewhere",
                "enough",
                "entirely",
                "especially",
                "et",
                "etc",
                "even",
                "ever",
                "every",
                "everybody",
                "everyone",
                "everything",
                "everywhere",
                "ex",
                "exactly",
                "example",
                "except",
                "far",
                "few",
                "fifth",
                "first",
                "five",
                "followed",
                "following",
                "follows",
                "for",
                "former",
                "formerly",
                "forth",
                "four",
                "from",
                "further",
                "furthermore",
                "get",
                "gets",
                "getting",
                "given",
                "gives",
                "go",
                "goes",
                "going",
                "gone",
                "got",
                "gotten",
                "greetings",
                "had",
                "hadn't",
                "happens",
                "hardly",
                "has",
                "hasn't",
                "have",
                "haven't",
                "having",
                "he",
                "he'd",
                "he'll",
                "hello",
                "help",
                "hence",
                "her",
                "here",
                "hereafter",
                "hereby",
                "herein",
                "here's",
                "hereupon",
                "hers",
                "herself",
                "he's",
                "hi",
                "him",
                "himself",
                "his",
                "hither",
                "hopefully",
                "how",
                "howbeit",
                "however",
                "how's",
                "i",
                "i'd",
                "ie",
                "if",
                "ignored",
                "i'll",
                "i'm",
                "immediate",
                "in",
                "inasmuch",
                "inc",
                "indeed",
                "indicate",
                "indicated",
                "indicates",
                "inner",
                "insofar",
                "instead",
                "into",
                "inward",
                "is",
                "isn't",
                "it",
                "it'd",
                "it'll",
                "its",
                "it's",
                "itself",
                "i've",
                "just",
                "keep",
                "keeps",
                "kept",
                "know",
                "known",
                "knows",
                "last",
                "lately",
                "later",
                "latter",
                "latterly",
                "least",
                "less",
                "lest",
                "let",
                "let's",
                "like",
                "liked",
                "likely",
                "little",
                "look",
                "looking",
                "looks",
                "ltd",
                "mainly",
                "many",
                "may",
                "maybe",
                "me",
                "mean",
                "meanwhile",
                "merely",
                "might",
                "more",
                "moreover",
                "most",
                "mostly",
                "much",
                "must",
                "mustn't",
                "my",
                "myself",
                "name",
                "namely",
                "nd",
                "near",
                "nearly",
                "necessary",
                "need",
                "needs",
                "neither",
                "never",
                "nevertheless",
                "new",
                "next",
                "nine",
                "no",
                "nobody",
                "non",
                "none",
                "noone",
                "nor",
                "normally",
                "not",
                "nothing",
                "novel",
                "now",
                "nowhere",
                "obviously",
                "of",
                "off",
                "often",
                "oh",
                "ok",
                "okay",
                "old",
                "on",
                "once",
                "one",
                "ones",
                "only",
                "onto",
                "or",
                "other",
                "others",
                "otherwise",
                "ought",
                "our",
                "ours",
                "ourselves",
                "out",
                "outside",
                "over",
                "overall",
                "own",
                "particular",
                "particularly",
                "per",
                "perhaps",
                "placed",
                "please",
                "plus",
                "possible",
                "presumably",
                "probably",
                "provides",
                "que",
                "quite",
                "qv",
                "rather",
                "rd",
                "re",
                "really",
                "reasonably",
                "regarding",
                "regardless",
                "regards",
                "relatively",
                "respectively",
                "right",
                "said",
                "same",
                "saw",
                "say",
                "saying",
                "says",
                "second",
                "secondly",
                "see",
                "seeing",
                "seem",
                "seemed",
                "seeming",
                "seems",
                "seen",
                "self",
                "selves",
                "sensible",
                "sent",
                "serious",
                "seriously",
                "seven",
                "several",
                "shall",
                "shan't",
                "she",
                "she'd",
                "she'll",
                "she's",
                "should",
                "shouldn't",
                "since",
                "six",
                "so",
                "some",
                "somebody",
                "somehow",
                "someone",
                "something",
                "sometime",
                "sometimes",
                "somewhat",
                "somewhere",
                "soon",
                "sorry",
                "specified",
                "specify",
                "specifying",
                "still",
                "sub",
                "such",
                "sup",
                "sure",
                "take",
                "taken",
                "tell",
                "tends",
                "th",
                "than",
                "thank",
                "thanks",
                "thanx",
                "that",
                "thats",
                "that's",
                "their",
                "theirs",
                "them",
                "themselves",
                "then",
                "thence",
                "there",
                "thereafter",
                "thereby",
                "therefore",
                "therein",
                "theres",
                "there's",
                "thereupon",
                "these",
                "they",
                "they'd",
                "they'll",
                "they're",
                "they've",
                "think",
                "third",
                "this",
                "thorough",
                "thoroughly",
                "those",
                "though",
                "three",
                "through",
                "throughout",
                "thru",
                "thus",
                "to",
                "together",
                "too",
                "took",
                "toward",
                "towards",
                "tried",
                "tries",
                "truly",
                "try",
                "trying",
                "t's","twice", "two", "un", "under","unfortunately",
                "unless","unlikely",
                "until","unto",
                "up", "upon", "us","use",
                "used",   "useful",
                "uses","using",    "usually", "value",  "various", "very",
                "via", "viz","vs", "want", "wants", "was", "wasn't","way", "we",
                "we'd", "welcome", "well", "we'll",
                "went", "were", "we're","weren't", "we've", "what",
                "whatever",  "what's","when","whence","whenever",
                "when's",  "where","whereafter",   "whereas", "whereby",  "wherein",  "where's",  "whereupon",
                "wherever", "whether", "which", "while", "whither", "who", "whoever",  "whole", "whom",
                "who's", "whose",  "why",  "why's","will", "willing", "wish", "with","within","without",
                "wonder","won't", "would", "wouldn't","yes","yet", "you","you'd", "you'll", "you're","yours", "your",
                "yourself","yourselves","you've","zero"]