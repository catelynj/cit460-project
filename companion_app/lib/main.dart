import 'dart:io';
import 'package:video_player/video_player.dart';
import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as path;
import 'package:permission_handler/permission_handler.dart';

final dio = Dio(
  BaseOptions(
    connectTimeout: Duration(seconds: 5),
    receiveTimeout: Duration(seconds: 5),
  ),
);
const piUrl = 'http://10.0.0.142:8000';

Future<String?> downloadMedia(Map<String, dynamic> item) async {
  try {
    final isVideo = item['type'] == 'video';
    final filename = item['filename'];
    final ext = isVideo ? 'mp4' : 'jpg';
    final saveFilename =
        '${isVideo ? 'video' : 'image'}_${DateTime.now().millisecondsSinceEpoch}.$ext';

    final dcimDir = Directory('/storage/emulated/0/DCIM/Testing');
    if (!await dcimDir.exists()) {
      await dcimDir.create(recursive: true);
    }

    final savePath = path.join(dcimDir.path, saveFilename);

    await dio.download(
      '$piUrl/download/$filename',
      savePath,
      onReceiveProgress: (received, total) {
        if (total != -1) {
          print('${(received / total * 100).toStringAsFixed(0)}%');
        }
      },
    );
    await Process.run('am', [
      'broadcast',
      '-a',
      'android.intent.action.MEDIA_SCANNER_SCAN_FILE',
      '-d',
      'file://$savePath',
    ]);

    return savePath;
  } catch (e) {
    print('Download failed: $e');
    return null;
  }
}

void main() {
  runApp(const MainApp());
}

class MainApp extends StatelessWidget {
  const MainApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.greenAccent,
          brightness: Brightness.dark,
        ),
      ),
      home: HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  var selectedIndex = 0;

  void _onDestinationSelected(int index) {
    setState(() {
      selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    Widget page;
    switch (selectedIndex) {
      case 0:
        page = Chat();
        break;
      case 1:
        page = Media();
        break;
      default:
        throw UnimplementedError('no widget for $selectedIndex');
    }

    return Scaffold(
      body: Row(
        children: [
          NavRail(
            selectedIndex: selectedIndex,
            onDestinationSelected: _onDestinationSelected,
          ),
          Expanded(child: page),
        ],
      ),
    );
  }
}

class Chat extends StatefulWidget {
  const Chat({super.key});
  @override
  State<Chat> createState() => _ChatState();
}

class _ChatState extends State<Chat> {
  List<Map<String, dynamic>> _chatHistory = [];
  final List<int> chatColors = <int>[800, 700, 600, 400, 200];

  Future<void> loadChatHistory() async {
    try {
      final response = await dio.get(
        '$piUrl/history',
        queryParameters: {'limit': 20},
      );

      if (mounted) {
        // check widget is still alive
        setState(() {
          _chatHistory = (response.data as List)
              .map((e) => Map<String, dynamic>.from(e))
              .toList();
        });
      }
    } catch (e) {
      print('Failed to load history: $e');
    }
  }

  @override
  void initState() {
    super.initState();
    Future.microtask(() => loadChatHistory());
  }

  // UPDATE: Modified structure to add RefreshIndicator from: https://stackoverflow.com/questions/57972505/pull-down-to-refresh-in-flutter
  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: loadChatHistory,
      child: ListView.builder(
        padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 70),
        itemCount: _chatHistory.length,
        itemBuilder: (BuildContext context, int index) {
          final item = _chatHistory[index];
          return ListTile(
            title: Text(item['query'] + '?'),
            subtitle: Text(item['response'] ?? 'No response'),
            minTileHeight: 80,
            isThreeLine: true,
            trailing: Text(
              item['queried_at'].substring(0, 10),
              style: TextStyle(fontSize: 10, color: Colors.blueGrey),
            ),
          );
        },
      ),
    );
  }
}

class Media extends StatefulWidget {
  const Media({super.key});
  @override
  State<Media> createState() => _MediaState();
}

class _MediaState extends State<Media> {
  // same implemntation as chat history
  List<Map<String, dynamic>> _mediaItems = [];
  bool _isLoading = true;
  String? _error;
  @override
  void initState() {
    super.initState();
    // make microtask to avoid app hang
    Future.microtask(() => loadAllMedia());
  }

  Future<void> loadAllMedia() async {
    try {
      final response = await dio.get('$piUrl/media');
      if (mounted) {
        setState(() {
          _mediaItems = (response.data['items'] as List)
              .map((e) => Map<String, dynamic>.from(e))
              .toList();
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'Could not load media.';
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) return Center(child: CircularProgressIndicator());
    if (_error != null) return Center(child: Text(_error!));

    return Column(
      children: [
        SizedBox(height: 50),
        Align(
          alignment: Alignment.topRight,
          child: ElevatedButton(
            onPressed: loadAllMedia,
            child: const Icon(Icons.refresh),
          ),
        ),
        Expanded(
          child: _mediaItems.isEmpty
              ? Center(child: Text('Nothing here yet!'))
              : GridView.builder(
                  padding: EdgeInsets.all(8),
                  gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    crossAxisSpacing: 10,
                    mainAxisSpacing: 4,
                  ),
                  itemCount: _mediaItems.length,
                  itemBuilder: (context, index) {
                    final item = _mediaItems[index];
                    final isVideo = item['type'] == 'video';
                    return GestureDetector(
                      onTap: () => _showFullScreen(item),
                      child: Stack(
                        fit: StackFit.expand,
                        children: [
                          Image.network(
                            '$piUrl${item['url']}',
                            fit: BoxFit.cover,
                            errorBuilder: (_, __, ___) =>
                                Container(color: Colors.grey[300]),
                          ),
                          if (isVideo)
                            Center(
                              child: Icon(
                                Icons.play_circle,
                                color: Colors.white,
                                size: 32,
                              ),
                            ),
                        ],
                      ),
                    );
                  },
                ),
        ),
      ],
    );
  }


// References:
// video_player | Flutter Package. (n.d.). Dart Packages. https://pub.dev/packages/video_player
  
  void _showFullScreen(Map<String, dynamic> item) {
    final isVideo = item['type'] == 'video';
    showDialog(
      context: context,
      builder: (_) => isVideo
          ? _VideoFullScreen(item: item)
          : _ImageFullScreen(item: item),
    );
  }
}

class _VideoFullScreen extends StatefulWidget {
  final Map<String, dynamic> item;
  const _VideoFullScreen({required this.item});

  @override
  State<_VideoFullScreen> createState() => _VideoFullScreenState();
}

class _VideoFullScreenState extends State<_VideoFullScreen> {
  late VideoPlayerController _controller;
  bool _isInitialized = false;

  // this section is very similar to API reference doc, just tailored to my code structure
  @override
  void initState() {
    super.initState();
    _controller = VideoPlayerController.networkUrl(
      Uri.parse('$piUrl${widget.item['url']}'),
    )..initialize().then((_) {
        if (mounted) setState(() => _isInitialized = true);
        _controller.play();
      });
  }

  // need to dispose controller to avoid memory leaks
  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // main structure is based on API reference
          _isInitialized
            // if its loaded, show controller
              ? AspectRatio(
                  aspectRatio: _controller.value.aspectRatio,
                  child: VideoPlayer(_controller),
                )
                // if its not, show loading symbol
              : const SizedBox(
                  height: 200,
                  child: Center(child: CircularProgressIndicator()),
                ),
          // play/pause button controls (API uses floating action button rather than icon)
          IconButton(
            icon: Icon(
              _controller.value.isPlaying ? Icons.pause : Icons.play_arrow,
            ),
            onPressed: () => setState(() {
              _controller.value.isPlaying
                  ? _controller.pause()
                  : _controller.play();
            }),
          ),
          Text(
            widget.item['filename'],
            style: const TextStyle(fontSize: 12, color: Colors.grey),
          ),
          TextButton(
            onPressed: () async {
              await Permission.storage.request();
              await downloadMedia(widget.item);
              if (context.mounted) Navigator.pop(context);
            },
            child: const Text('Download'),
          ),
        ],
      ),
    );
  }
}

// same general structure as video, just simpler
class _ImageFullScreen extends StatelessWidget {
  final Map<String, dynamic> item;
  const _ImageFullScreen({required this.item});

  @override
  Widget build(BuildContext context) {
    return Dialog(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Image.network('$piUrl${item['url']}'),
          Text(
            item['filename'],
            style: const TextStyle(fontSize: 12, color: Colors.grey),
          ),
          TextButton(
            onPressed: () async {
              await Permission.storage.request();
              await downloadMedia(item);
              if (context.mounted) Navigator.pop(context);
            },
            child: const Text('Download'),
          ),
        ],
      ),
    );
  }
}

class NavRail extends StatelessWidget {
  const NavRail({
    super.key,
    required this.selectedIndex,
    required this.onDestinationSelected,
  });

  final int selectedIndex;
  final ValueChanged<int> onDestinationSelected;

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Row(
        children: [
          NavigationRail(
            selectedIndex: selectedIndex,
            onDestinationSelected: onDestinationSelected,
            destinations: const <NavigationRailDestination>[
              NavigationRailDestination(
                icon: Icon(Icons.text_snippet_outlined),
                selectedIcon: Icon(Icons.text_snippet),
                label: Text('Chat'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.photo_album_outlined),
                selectedIcon: Icon(Icons.photo_album_rounded),
                label: Text('Media'),
              ),
            ],
          ),
          const VerticalDivider(thickness: 1, width: 1),
        ],
      ),
    );
  }
}
