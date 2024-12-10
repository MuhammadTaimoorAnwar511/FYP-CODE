import React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import BarChartIcon from '@mui/icons-material/BarChart';
import TimelineIcon from '@mui/icons-material/Timeline';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import NoteIcon from '@mui/icons-material/Note';

const Navbar = () => {
    return (
        <AppBar position="static">
            <Toolbar>
                <Typography variant="h6" sx={{ flexGrow: 1 }}>
                    {/* Trading Platform */}
                </Typography>
                <Box>
                    <Button
                        color="inherit"
                        startIcon={<AccountCircleIcon />}
                        sx={{ margin: '0 8px' }}
                    >
                        Profile
                    </Button>
                    <Button
                        color="inherit"
                        startIcon={<BarChartIcon />}
                        sx={{ margin: '0 8px' }}
                    >
                        Market Overview
                    </Button>
                    <Button
                        color="inherit"
                        startIcon={<TimelineIcon />}
                        sx={{ margin: '0 8px' }}
                    >
                        Chart
                    </Button>
                    <Button
                        color="inherit"
                        startIcon={<SmartToyIcon />}
                        sx={{ margin: '0 8px' }}
                    >
                        Bot
                    </Button>
                    <Button
                        color="inherit"
                        startIcon={<NoteIcon />}
                        sx={{ margin: '0 8px' }}
                    >
                        Trading Journals
                    </Button>
                </Box>
            </Toolbar>
        </AppBar>
    );
};

export default Navbar;
