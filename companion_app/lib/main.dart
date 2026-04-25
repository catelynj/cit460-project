import 'dart:io';

import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import 'package:path_provider/path_provider.dart';

final dio = Dio();
const piUrl = 'http://10.0.0.142:8000';

Future<String?> downloadLatestMedia() async {
  final metaResponse = await dio.get('$piUrl/media/latest');
  final filename = metaResponse.data['filename'];
  final fileType = metaResponse.data['type'];

  final dir = await getApplicationDocumentsDirectory();
  final savePath = '${dir.path}/$filename';

  await dio.download(
    '$piUrl/download/$filename',
    savePath,
    onReceiveProgress: (received, total) {
      if (total != -1) {
        print(
          'Download progress: ${(received / total * 100).toStringAsFixed(0)}%',
        );
      }
    },
  );

  print('Saved $fileType to $savePath');
  return savePath;
}

void main() {
  runApp(const MainApp());
}

class MainApp extends StatelessWidget {
  const MainApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(home: HomePage());
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
  final List<String> chats = <String>['Chat 1', 'Chat 2', 'Chat 3'];
  final List<int> chatColors = <int>[600, 400, 200];
  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 50),
      itemCount: chats.length,
      itemBuilder: (BuildContext context, int index) {
        return Container(
          height: 150,
          color: Colors.deepPurple[chatColors[index]],
          child: Center(child: Text(chats[index])),
        );
      },
    );
  }
}

class Media extends StatefulWidget {
  const Media({super.key});
  @override
  State<Media> createState() => _MediaState();
}

class _MediaState extends State<Media> {
  String? _latestFilePath;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        children: [
          SizedBox(height: 50),
          Align(
            alignment: Alignment.topRight,
            child: ElevatedButton(
              onPressed: () async {
                final path = await downloadLatestMedia();
                if (path != null) {
                  setState(() => _latestFilePath = path);
                }
              },
              child: const Icon(Icons.refresh),
            ),
          ),
          SizedBox(height: 350),
          Align(
            alignment: Alignment.center,
            child: _latestFilePath != null
                ? Image.file(File(_latestFilePath!))
                : Text('Nothing here yet!'),
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
